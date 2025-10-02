#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Undistort a dashcam video using single-image plumb-line calibration with
a 1-parameter radial division model.

Two modes:
  (1) --auto-calib-frames K : sample K frames from the video, detect long lines,
      estimate lambda (and optionally principal point), then undistort all frames.
  (2) --calib-json file.json: load precomputed {cx, cy, lambda} and apply to all frames.

Audio: OpenCV does not handle audio. If --copy-audio is set and ffmpeg is available,
       the script will remux the original audio into the output video after processing.

Model (division):
  p_u = p_d / (1 + λ * r_d^2), with r_d^2 computed in normalized coords w.r.t principal point.
Inverse mapping (closed-form) used for remap (undistorted -> distorted):
  α = [1 - sqrt(1 - 4 λ r_u^2)] / (2 λ r_u^2), α -> 1 as λ -> 0.

Author: (you)
"""

import argparse
import json
import math
import os
import shutil
import subprocess
from typing import List, Tuple

import cv2
import numpy as np

# -----------------------------
# Geometry & model helpers
# -----------------------------

def sample_points_on_segment(p1, p2, num=20):
    p1 = np.asarray(p1, dtype=np.float32)
    p2 = np.asarray(p2, dtype=np.float32)
    t = np.linspace(0.0, 1.0, num, dtype=np.float32)[:, None]
    pts = p1[None, :] * (1 - t) + p2[None, :] * t
    return pts

def best_fit_line_residuals(points):
    P = np.asarray(points, dtype=np.float64)
    c = P.mean(axis=0)
    Q = P - c
    # SVD of covariance
    _, _, VT = np.linalg.svd(Q, full_matrices=False)
    d = VT[0, :]
    proj = (Q @ d[:, None]) * d[None, :]
    orth = Q - proj
    residuals = np.sqrt((orth ** 2).sum(axis=1))
    sse = float((residuals ** 2).sum())
    return residuals, sse

def undistort_points_division(points_px, cx, cy, scale_norm, lam):
    P = np.asarray(points_px, dtype=np.float64)
    x = (P[:, 0] - cx) / scale_norm
    y = (P[:, 1] - cy) / scale_norm
    r2 = x * x + y * y
    denom = 1.0 + lam * r2
    if np.any(denom <= 1e-9):
        return np.full_like(P, np.nan)
    xu = x / denom
    yu = y / denom
    Pu = np.column_stack([xu * scale_norm + cx, yu * scale_norm + cy])
    return Pu

def build_inverse_remap_division(H, W, cx, cy, scale_norm, lam, zoom=1.0):
    uu, vv = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    if zoom != 1.0:
        uu = (uu - cx) / zoom + cx
        vv = (vv - cy) / zoom + cy
    x_u = (uu - cx) / scale_norm
    y_u = (vv - cy) / scale_norm
    r2_u = x_u * x_u + y_u * y_u

    if abs(lam) < 1e-12:
        alpha = np.ones_like(r2_u, dtype=np.float32)
    else:
        disc = np.maximum(1.0 - 4.0 * lam * r2_u, 0.0)
        sqrt_disc = np.sqrt(disc, dtype=np.float32)
        denom = 2.0 * lam * r2_u
        near_zero = (r2_u < 1e-12)
        alpha = np.empty_like(r2_u, dtype=np.float32)
        safe = ~near_zero
        alpha[safe] = (1.0 - sqrt_disc[safe]) / denom[safe]
        alpha[near_zero] = 1.0

    x_d = alpha * x_u
    y_d = alpha * y_u
    map_x = (x_d * scale_norm + cx).astype(np.float32)
    map_y = (y_d * scale_norm + cy).astype(np.float32)
    return map_x, map_y

# -----------------------------
# Line detection (LSD with fallback)
# -----------------------------

def detect_line_segments(img_gray, min_length_px):
    """
    Returns segments [(x1,y1,x2,y2), ...] filtered by length.
    Tries LSD, falls back to HoughLinesP if unavailable.
    """
    segments = []
    lsd = None
    if hasattr(cv2, "createLineSegmentDetector"):
        try:
            lsd = cv2.createLineSegmentDetector(_refine=cv2.LSD_REFINE_STD)
        except Exception:
            lsd = None

    if lsd is not None:
        lines, _, _, _ = lsd.detect(img_gray)
        if lines is not None:
            for l in lines:
                x1, y1, x2, y2 = l[0]
                length = math.hypot(x2 - x1, y2 - y1)
                if length >= min_length_px:
                    segments.append((float(x1), float(y1), float(x2), float(y2)))
        return segments

    # Fallback: use Canny + probabilistic Hough
    edges = cv2.Canny(img_gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=60,
                            minLineLength=int(min_length_px), maxLineGap=10)
    if lines is not None:
        for l in lines:
            x1, y1, x2, y2 = l[0]
            length = math.hypot(x2 - x1, y2 - y1)
            if length >= min_length_px:
                segments.append((float(x1), float(y1), float(x2), float(y2)))
    return segments

def draw_segments(img, segments, color=(0, 255, 0), thickness=2):
    out = img.copy()
    for (x1, y1, x2, y2) in segments:
        cv2.line(out, (int(round(x1)), int(round(y1))),
                      (int(round(x2)), int(round(y2))), color, thickness, cv2.LINE_AA)
    return out

# -----------------------------
# Objective & optimization
# -----------------------------

def straightness_cost_for_lambda(lam, segments, cx, cy, scale_norm, samples_per_segment=25):
    total_sse = 0.0
    valid_any = False
    for (x1, y1, x2, y2) in segments:
        pts_d = sample_points_on_segment((x1, y1), (x2, y2), num=samples_per_segment)
        pts_u = undistort_points_division(pts_d, cx, cy, scale_norm, lam)
        if np.any(np.isnan(pts_u)):
            return 1e50
        _, sse = best_fit_line_residuals(pts_u)
        seg_len = math.hypot(x2 - x1, y2 - y1)
        total_sse += sse * (1.0 + 0.001 * seg_len)
        valid_any = True
    if not valid_any:
        return 1e50
    return total_sse

def coarse_to_fine_lambda_search(segments, cx, cy, scale_norm,
                                 lam_lo=-0.8, lam_hi=0.8, iters=3, grid_points=41):
    lo, hi = lam_lo, lam_hi
    best_lam, best_cost = None, float('inf')
    for _ in range(iters):
        grid = np.linspace(lo, hi, grid_points)
        costs = []
        for lam in grid:
            c = straightness_cost_for_lambda(float(lam), segments, cx, cy, scale_norm)
            costs.append(c)
            if c < best_cost:
                best_cost, best_lam = c, float(lam)
        idx = int(np.argmin(costs))
        left = max(0, idx - 2)
        right = min(len(grid) - 1, idx + 2)
        lo, hi = float(grid[left]), float(grid[right])
        if abs(hi - lo) < 1e-5:
            break
    return best_lam, best_cost

def refine_principal_point(img_shape, segments, cx0, cy0, scale_norm,
                           lam_bounds=(-0.8, 0.8), grid_frac=0.03, steps=3):
    H, W = img_shape[:2]
    dx = int(round(W * grid_frac))
    dy = int(round(H * grid_frac))
    xs = np.linspace(cx0 - dx, cx0 + dx, steps)
    ys = np.linspace(cy0 - dy, cy0 + dy, steps)
    best = {'cost': float('inf'), 'cx': cx0, 'cy': cy0, 'lam': 0.0}
    for cx in xs:
        for cy in ys:
            lam, cost = coarse_to_fine_lambda_search(segments, cx, cy, scale_norm,
                                                     lam_lo=lam_bounds[0], lam_hi=lam_bounds[1])
            if cost < best['cost']:
                best.update({'cost': cost, 'cx': float(cx), 'cy': float(cy), 'lam': float(lam)})
    return best['cx'], best['cy'], best['lam'], best['cost']

# -----------------------------
# Calibration from video frames
# -----------------------------

def pick_sample_indices(n_frames, k, margin_ratio=0.1):
    """Pick k indices spaced across the video, avoiding edges where keyframes may be sparse."""
    if n_frames <= 0 or k <= 0:
        return []
    start = int(n_frames * margin_ratio)
    end = max(start + 1, int(n_frames * (1 - margin_ratio)))
    if end <= start:
        start, end = 0, n_frames
    if k >= (end - start):
        return list(range(start, end))
    return list(np.linspace(start, end - 1, k, dtype=int))

def accumulate_segments_from_frames(cap, indices, min_len_px, max_segments=1200, visualize=False, vis_dir=None):
    segments_all = []
    thumbs = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        segs = detect_line_segments(gray, min_length_px=min_len_px)
        segs = sorted(segs, key=lambda s: -math.hypot(s[2] - s[0], s[3] - s[1]))
        # Keep top N per frame to avoid bias
        segs = segs[: min(200, len(segs))]
        segments_all.extend(segs)

        if visualize and vis_dir is not None:
            os.makedirs(vis_dir, exist_ok=True)
            overlay = draw_segments(frame, segs, (0, 255, 0), 2)
            outp = os.path.join(vis_dir, f"segments_frame_{idx:06d}.jpg")
            cv2.imwrite(outp, overlay)
            thumbs.append(outp)

        if len(segments_all) >= max_segments:
            break

    # Global cap to control optimization cost
    segments_all = sorted(segments_all, key=lambda s: -math.hypot(s[2] - s[0], s[3] - s[1]))
    segments_all = segments_all[:max_segments]
    return segments_all

# -----------------------------
# Audio remux helper (optional)
# -----------------------------

def remux_audio_with_ffmpeg(src_video, silent_video, out_video):
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        print("[WARN] ffmpeg not found on PATH; output will be silent.")
        # Move silent_video to out_video if needed
        if silent_video != out_video:
            shutil.move(silent_video, out_video)
        return True
    cmd = [
        ffmpeg, "-y",
        "-i", src_video,
        "-i", silent_video,
        "-c", "copy",
        "-map", "1:v:0",
        "-map", "0:a?",
        "-shortest",
        out_video
    ]
    print("[INFO] Remuxing audio with ffmpeg...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        print("[WARN] ffmpeg remux failed; keeping silent video.")
        if silent_video != out_video:
            shutil.move(silent_video, out_video)
    else:
        # Remove temp silent file if different
        if silent_video != out_video and os.path.exists(silent_video):
            os.remove(silent_video)
    return True

# -----------------------------
# Main
# -----------------------------

def main():
    ap = argparse.ArgumentParser(description="Undistort a dashcam video using single-image plumb-line calibration.")
    ap.add_argument("--input", required=True, help="Path to input distorted video.")
    ap.add_argument("--output", required=True, help="Path to output undistorted video (mp4/avi).")
    ap.add_argument("--auto-calib-frames", type=int, default=0, help="If >0, auto-calibrate from K sampled frames.")
    ap.add_argument("--pp-refine", action="store_true", help="Refine principal point during calibration.")
    ap.add_argument("--lambda-bounds", nargs=2, type=float, default=[-0.8, 0.8], help="Search bounds for lambda.")
    ap.add_argument("--calib-json", help="Optional JSON with {'width','height','cx','cy','lambda'}. If provided, skips auto-calib.")
    ap.add_argument("--save-calib", help="Path to save estimated calibration JSON.")
    ap.add_argument("--zoom", type=float, default=1.0, help="Canvas zoom for undistortion.")
    ap.add_argument("--fourcc", default="mp4v", help="FOURCC for output video (e.g., mp4v, avc1, XVID).")
    ap.add_argument("--visualize-segments", action="store_true", help="Save overlays of detected lines used in calibration.")
    ap.add_argument("--copy-audio", action="store_true", help="Try to copy audio track using ffmpeg.")
    args = ap.parse_args()

    # Open input
    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {args.input}")

    # Properties
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if fps <= 0 or fps != fps:  # NaN check
        fps = 30.0  # default fallback

    print(f"[INFO] Video: {W}x{H} @ {fps:.3f} FPS, frames={n_frames}")

    cx = W * 0.5
    cy = H * 0.5
    scale_norm = float(max(W, H))
    lam = 0.0

    # Load calibration or estimate from frames
    if args.calib_json:
        with open(args.calib_json, "r", encoding="utf-8") as f:
            calib = json.load(f)
        # Basic validation
        if int(calib.get("width", W)) != W or int(calib.get("height", H)) != H:
            print("[WARN] Calibration resolution does not match video. "
                  "Proceeding, but results may be suboptimal.")
        cx = float(calib["cx"]); cy = float(calib["cy"]); lam = float(calib["lambda"])
        print(f"[INFO] Loaded calibration: cx={cx:.2f}, cy={cy:.2f}, lambda={lam:.6f}")

    else:
        K = args.auto_calib_frames if args.auto_calib_frames > 0 else 6
        indices = pick_sample_indices(n_frames, K, margin_ratio=0.10)
        min_len = 0.05 * math.hypot(W, H)  # ~5% of diagonal
        vis_dir = None
        if args.visualize_segments:
            base = os.path.splitext(args.output)[0]
            vis_dir = base + "_calib_segments"
        print(f"[INFO] Sampling {len(indices)} frames for calibration...")
        segments = accumulate_segments_from_frames(cap, indices, min_len_px=min_len,
                                                   max_segments=1400,
                                                   visualize=args.visualize_segments, vis_dir=vis_dir)
        if len(segments) < 10:
            print("[WARN] Very few line segments detected; calibration may be unreliable.")
        lam_lo, lam_hi = float(args.lambda_bounds[0]), float(args.lambda_bounds[1])
        if args.pp_refine:
            cx, cy, lam, cost = refine_principal_point((H, W, 3), segments, cx, cy, scale_norm,
                                                       lam_bounds=(lam_lo, lam_hi),
                                                       grid_frac=0.03, steps=3)
            print(f"[INFO] Refined PP: cx={cx:.2f}, cy={cy:.2f}, lambda={lam:.6f}, cost={cost:.3e}")
        else:
            lam, cost = coarse_to_fine_lambda_search(segments, cx, cy, scale_norm,
                                                     lam_lo=lam_lo, lam_hi=lam_hi)
            print(f"[INFO] Estimated lambda={lam:.6f} with PP at center. Cost={cost:.3e}")

        if args.save_calib:
            calib = {"width": W, "height": H, "cx": cx, "cy": cy, "lambda": lam, "scale_norm": scale_norm}
            with open(args.save_calib, "w", encoding="utf-8") as f:
                json.dump(calib, f, indent=2)
            print(f"[OK] Saved calibration to {args.save_calib}")

    # Build remap once
    print("[INFO] Building remap...")
    map_x, map_y = build_inverse_remap_division(H, W, cx, cy, scale_norm, lam, zoom=args.zoom)

    # Prepare output writer (write silent first; audio remux later if requested)
    silent_tmp = args.output
    if args.copy_audio:
        root, ext = os.path.splitext(args.output)
        silent_tmp = root + "_silent" + ext

    fourcc = cv2.VideoWriter_fourcc(*args.fourcc)
    writer = cv2.VideoWriter(silent_tmp, fourcc, fps, (W, H))
    if not writer.isOpened():
        raise RuntimeError("Failed to open VideoWriter. Try a different --fourcc (e.g., 'XVID' or 'avc1').")

    # Process frames
    print("[INFO] Undistorting frames...")
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok or frame is None:
            break
        undist = cv2.remap(frame, map_x, map_y, interpolation=cv2.INTER_CUBIC,
                           borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
        writer.write(undist)
        frame_idx += 1
        if frame_idx % 100 == 0:
            print(f"  processed {frame_idx}/{n_frames if n_frames>0 else '?'} frames")

    writer.release()
    cap.release()
    print(f"[OK] Wrote silent video: {silent_tmp}")

    # Optional: remux audio
    if args.copy_audio:
        remux_audio_with_ffmpeg(args.input, silent_tmp, args.output)
        print(f"[OK] Final video with audio: {args.output}")

if __name__ == "__main__":
    main()

