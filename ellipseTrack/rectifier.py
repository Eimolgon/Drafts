#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Self-calibrated lens distortion correction for a monocular video (no known intrinsics).

Approach:
- Use a 1-parameter division model for radial distortion: 
      (x_d, y_d) = (x_u, y_u) / (1 + λ * r_u^2),
  where r_u is radius in undistorted normalized pixel coordinates.
- Estimate λ (and optionally the principal point (cx, cy)) by maximizing the total length
  of straight lines detected by Hough in undistorted frames (plumbline heuristic).

This works best when the video contains many straight edges (e.g., buildings, poles, horizons).

Author: (you)
"""

import argparse
import math
import sys
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional

import cv2
import numpy as np
from scipy.ndimage import median_filter


# --------------------------
# Utility dataclasses
# --------------------------
@dataclass
class EstimationParams:
    sample_frames: int = 20
    downscale_width: int = 640
    optimize_center: bool = False
    center_search_px: int = 0  # computed as ~3% of dim if optimize_center=True
    lambda_min: float = -0.6
    lambda_max: float = 0.6
    lambda_coarse_step: float = 0.02
    lambda_fine_window: float = 0.05
    lambda_fine_step: float = 0.005
    regularization: float = 0.0  # optional L2 reg on lambda
    canny_low_frac: float = 0.66  # auto-canny fraction around median
    canny_high_frac: float = 1.33
    hough_threshold: int = 50
    hough_min_line_frac: float = 0.05  # fraction of min(W,H)
    hough_max_gap_frac: float = 0.01   # fraction of min(W,H)
    max_frames_for_estimation: int = 50  # hard cap for safety


@dataclass
class VideoInfo:
    width: int
    height: int
    fps: float
    frame_count: int


@dataclass
class EstimationResult:
    lam: float
    cx: float
    cy: float
    score: float


# --------------------------
# Image geometry / remap
# --------------------------
def compute_division_model_maps(
    width: int, height: int, lam: float, cx: float, cy: float
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Precompute remap maps (map_x, map_y) for cv2.remap using the division model.
    We map target (undistorted) pixel to source (distorted) coordinate.

    Normalization:
        We use radius normalized by half-diagonal so that lambda is scale-stable.

    Args:
        width, height: output (undistorted) image size (usually same as input).
        lam: division model parameter (lambda).
        cx, cy: principal point in pixel coords (source image).
    """
    # Create grid of undistorted pixel coordinates relative to principal point
    xs = np.arange(width, dtype=np.float32)
    ys = np.arange(height, dtype=np.float32)
    X, Y = np.meshgrid(xs, ys)

    dx = X - cx
    dy = Y - cy

    # Normalize by half-diagonal radius for scale invariance
    R = 0.5 * math.hypot(width, height)
    r2n = (dx * dx + dy * dy) / (R * R)  # r^2 normalized

    denom = (1.0 + lam * r2n).astype(np.float32)
    denom = np.where(denom == 0, 1e-8, denom)

    # Division model mapping (undistorted -> distorted)
    map_x = (dx / denom + cx).astype(np.float32)
    map_y = (dy / denom + cy).astype(np.float32)

    return map_x, map_y


def undistort_image_division(
    img: np.ndarray, lam: float, cx: float, cy: float, interpolation=cv2.INTER_LINEAR
) -> np.ndarray:
    """Apply division-model undistortion by building remap maps on-the-fly."""
    h, w = img.shape[:2]
    map_x, map_y = compute_division_model_maps(w, h, lam, cx, cy)
    undist = cv2.remap(img, map_x, map_y, interpolation, borderMode=cv2.BORDER_REPLICATE)
    return undist


# --------------------------
# Edge/line-based scoring
# --------------------------
def auto_canny(gray: np.ndarray, low_frac=0.66, high_frac=1.33) -> np.ndarray:
    """Auto Canny thresholds based on the median."""
    med = np.median(gray)
    lower = max(0, int(low_frac * med))
    upper = min(255, int(high_frac * med))
    edges = cv2.Canny(gray, lower, upper, apertureSize=3, L2gradient=True)
    return edges


def hough_line_length_score(
    img: np.ndarray,
    threshold: int = 50,
    min_line_frac: float = 0.05,
    max_gap_frac: float = 0.01,
    canny_low_frac: float = 0.66,
    canny_high_frac: float = 1.33,
) -> float:
    """
    Score the image by total length of detected line segments after Canny+Hough.
    Longer lines => stronger evidence of restored straightness.

    Returns:
        Total length in pixels (float)
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img.copy()
    # Denoise a bit to stabilize edges across parameters
    gray = median_filter(gray, size=3).astype(np.uint8)
    edges = auto_canny(gray, canny_low_frac, canny_high_frac)

    h, w = gray.shape[:2]
    min_dim = min(h, w)
    min_line_len = max(10, int(min_line_frac * min_dim))
    max_line_gap = max(2, int(max_gap_frac * min_dim))

    lines = cv2.HoughLinesP(
        edges, rho=1, theta=np.pi / 180.0,
        threshold=threshold,
        minLineLength=min_line_len,
        maxLineGap=max_line_gap
    )
    if lines is None:
        return 0.0

    total = 0.0
    for l in lines[:, 0, :]:
        x1, y1, x2, y2 = l
        total += math.hypot(x2 - x1, y2 - y1)
    return float(total)


# --------------------------
# Parameter estimation
# --------------------------
def sample_frame_indices(n_total: int, n_samples: int) -> List[int]:
    """Evenly sample frame indices from [0, n_total-1]."""
    if n_samples <= 1:
        return [n_total // 2]
    step = max(1, n_total // n_samples)
    idxs = list(range(0, n_total, step))
    if len(idxs) > n_samples:
        idxs = idxs[:n_samples]
    if not idxs:
        idxs = [0]
    return idxs


def downscale_keep_aspect(img: np.ndarray, target_width: int) -> np.ndarray:
    h, w = img.shape[:2]
    if w <= target_width:
        return img
    scale = target_width / float(w)
    new_w = target_width
    new_h = int(round(h * scale))
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def get_video_info(cap: cv2.VideoCapture) -> VideoInfo:
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = float(cap.get(cv2.CAP_PROP_FPS)) or 30.0
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    return VideoInfo(width=w, height=h, fps=fps, frame_count=count)


def compute_score_for_lambda(
    frames_small: List[np.ndarray],
    lam: float,
    cx: float,
    cy: float,
    ep: EstimationParams
) -> float:
    """Apply undistortion with (lam, cx, cy) to frames and compute aggregated line-length score."""
    score = 0.0
    for img in frames_small:
        und = undistort_image_division(img, lam, cx, cy, interpolation=cv2.INTER_LINEAR)
        score += hough_line_length_score(
            und,
            threshold=ep.hough_threshold,
            min_line_frac=ep.hough_min_line_frac,
            max_gap_frac=ep.hough_max_gap_frac,
            canny_low_frac=ep.canny_low_frac,
            canny_high_frac=ep.canny_high_frac,
        )
    # Optional regularization to avoid absurd magnitudes
    score -= ep.regularization * (lam * lam)
    return score


def estimate_lambda_and_center(
    frames_small: List[np.ndarray], ep: EstimationParams
) -> EstimationResult:
    """
    Coarse-to-fine search over lambda. Optionally searches around image center.
    Returns best (lam, cx, cy, score) in the coordinate system of frames_small.
    """
    if not frames_small:
        raise ValueError("No frames provided for estimation.")

    h, w = frames_small[0].shape[:2]
    cx0, cy0 = w / 2.0, h / 2.0

    # Center search grid
    center_offsets = [(0, 0)]
    if ep.optimize_center:
        max_off = int(round(0.03 * min(w, h)))  # ±3% of min dim
        ep.center_search_px = max_off
        grid = [-max_off, 0, max_off]
        center_offsets = [(dx, dy) for dx in grid for dy in grid]

    best = EstimationResult(lam=0.0, cx=cx0, cy=cy0, score=-1e18)

    # For each candidate center
    for (dx, dy) in center_offsets:
        cx = cx0 + dx
        cy = cy0 + dy

        # Coarse grid search for lambda
        lam_candidates = np.arange(ep.lambda_min, ep.lambda_max + 1e-9, ep.lambda_coarse_step)
        coarse_scores = []
        best_lam = None
        best_score = -1e18

        for lam in lam_candidates:
            s = compute_score_for_lambda(frames_small, lam, cx, cy, ep)
            coarse_scores.append((lam, s))
            if s > best_score:
                best_score = s
                best_lam = lam

        # Fine search around the best coarse lambda
        lam_lo = max(ep.lambda_min, best_lam - ep.lambda_fine_window)
        lam_hi = min(ep.lambda_max, best_lam + ep.lambda_fine_window)
        lam_refine = np.arange(lam_lo, lam_hi + 1e-12, ep.lambda_fine_step)

        for lam in lam_refine:
            s = compute_score_for_lambda(frames_small, lam, cx, cy, ep)
            if s > best_score:
                best_score = s
                best_lam = lam

        # Track best across centers
        if best_score > best.score:
            best = EstimationResult(lam=best_lam, cx=cx, cy=cy, score=best_score)

    return best


# --------------------------
# Main processing
# --------------------------
def process_video(
    input_path: str,
    output_path: str,
    sample_frames: int = 20,
    downscale_width: int = 640,
    optimize_center: bool = False,
    preview: int = 0,
) -> None:
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open input video: {input_path}")

    info = get_video_info(cap)
    if info.frame_count <= 0:
        # Some containers don't have frame count; we will try to iterate anyway.
        info = VideoInfo(width=info.width, height=info.height, fps=info.fps, frame_count=300)

    print(f"[INFO] Input: {input_path}")
    print(f"[INFO] Resolution: {info.width}x{info.height} @ {info.fps:.2f} FPS, frames: {info.frame_count}")

    # ---- Sample frames for estimation ----
    ep = EstimationParams(sample_frames=sample_frames, downscale_width=downscale_width, optimize_center=optimize_center)
    n_samples = min(ep.sample_frames, ep.max_frames_for_estimation, max(1, info.frame_count))
    frame_idxs = sample_frame_indices(info.frame_count, n_samples)

    frames_small: List[np.ndarray] = []
    print(f"[INFO] Sampling {len(frame_idxs)} frames for parameter estimation...")
    for idx in frame_idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        small = downscale_keep_aspect(frame, ep.downscale_width)
        frames_small.append(small)

    if not frames_small:
        raise RuntimeError("Failed to read sample frames for estimation.")

    # ---- Estimate lambda (and center on the small frames) ----
    print("[INFO] Estimating distortion parameter (this may take a few minutes)...")
    t0 = time.time()
    est_small = estimate_lambda_and_center(frames_small, ep)
    t1 = time.time()
    print(f"[INFO] Estimation done in {t1 - t0:.1f}s")
    print(f"[INFO] Estimated lambda: {est_small.lam:.6f}")
    print(f"[INFO] Estimated center (small-res): cx={est_small.cx:.1f}, cy={est_small.cy:.1f}")

    # ---- Lift center from small-res to full-res coordinates ----
    # Since we used downscaled frames, rescale cx, cy to full res.
    # We assume uniform downscale by width.
    small_h, small_w = frames_small[0].shape[:2]
    scale = info.width / float(small_w)
    cx_full = est_small.cx * scale
    cy_full = est_small.cy * scale
    lam = est_small.lam

    print(f"[INFO] Using full-res principal point: cx={cx_full:.1f}, cy={cy_full:.1f}")

    # ---- Precompute full-resolution remap ----
    print("[INFO] Precomputing undistortion maps at full resolution...")
    map_x, map_y = compute_division_model_maps(info.width, info.height, lam, cx_full, cy_full)

    # ---- Prepare output video ----
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # widely compatible
    out = cv2.VideoWriter(output_path, fourcc, info.fps, (info.width, info.height))
    if not out.isOpened():
        raise RuntimeError(f"Could not open output video for writing: {output_path}")

    # Reset capture to start
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if info.frame_count > 0 else -1
    frame_id = 0

    print("[INFO] Writing corrected video...")
    while True:
        ok, frame = cap.read()
        if not ok or frame is None:
            break

        und = cv2.remap(frame, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        out.write(und)

        if preview > 0:
            concat = np.hstack([frame, und])
            disp = downscale_keep_aspect(concat, 1280)
            cv2.imshow("Original (left)  |  Undistorted (right)", disp)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit preview
                preview = 0
                cv2.destroyAllWindows()

        frame_id += 1
        if frame_id % 50 == 0 and total > 0:
            pct = 100.0 * frame_id / total
            sys.stdout.write(f"\r[INFO] Progress: {pct:5.1f}%")
            sys.stdout.flush()

    if total > 0:
        sys.stdout.write("\r[INFO] Progress: 100.0%\n")
        sys.stdout.flush()

    cap.release()
    out.release()
    if preview > 0:
        cv2.destroyAllWindows()

    print(f"[INFO] Saved corrected video to: {output_path}")
    print(f"[INFO] Final parameters: lambda={lam:.6f}, cx={cx_full:.1f}, cy={cy_full:.1f}")


# --------------------------
# CLI
# --------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Lens distortion correction without calibration (division model).")
    p.add_argument("input", type=str, help="Path to input video.")
    p.add_argument("--output", type=str, default="corrected.mp4", help="Path to output video.")
    p.add_argument("--sample-frames", type=int, default=20, help="Number of frames to sample for estimation.")
    p.add_argument("--downscale-width", type=int, default=640, help="Downscale width used during estimation.")
    p.add_argument("--optimize-center", action="store_true", help="Also search small offsets around image center.")
    p.add_argument("--preview", type=int, default=0, help=">0 to preview side-by-side during writing.")
    return p.parse_args()


def main():
    args = parse_args()
    process_video(
        input_path=args.input,
        output_path=args.output,
        sample_frames=args.sample_frames,
        downscale_width=args.downscale_width,
        optimize_center=args.optimize_center,
        preview=args.preview,
    )


if __name__ == "__main__":
    main()
