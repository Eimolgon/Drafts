import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2
from glob import glob

# -------- CONFIG --------
# directory with YOLO .txt files
label_dir = "/home/eimolgon/Documents/Drafts/ellipseTrack/Data/5-ytcrash-yolo/labels/train"
image_dims = (1280, 720)         # (width, height) for denormalizing
class_names = ["front_wheel", "rear_wheel"]
# ------------------------

def load_segments_from_txt(file_path):
    ellipses = []
    with open(file_path, "r") as f:
        for line in f:
            tokens = line.strip().split()
            if len(tokens) < 11:
                continue  # skip malformed or very short lines
            class_id = int(tokens[0])
            coords = list(map(float, tokens[1:]))
            points = np.array(coords).reshape(-1, 2)
            ellipses.append((class_id, points))
    return ellipses

def fit_ellipse(points, image_dims):
    w, h = image_dims
    pts = np.array([[x * w, y * h] for x, y in points], dtype=np.float32)
    if len(pts) < 5:
        return None
    pts = pts.reshape(-1, 1, 2)  # required shape for OpenCV
    try:
        (cx, cy), (MA, ma), angle = cv2.fitEllipse(pts)
        return cx, cy, MA, ma, angle
    except cv2.error as e:
        print("OpenCV fitEllipse failed:", e)
        return None


# Collect all .txt files and sort by frame number
label_files = sorted(glob(os.path.join(label_dir, "*.txt")))

records = []

for i, file_path in enumerate(label_files):
    frame_num = i
    segments = load_segments_from_txt(file_path)
    
    for class_id, norm_pts in segments:
        result = fit_ellipse(norm_pts, image_dims)
        if result:
            cx, cy, MA, ma, angle = result
            records.append({
                "frame": frame_num,
                "label": class_names[class_id],
                "cx": cx,
                "cy": cy,
                "major_axis": MA,
                "minor_axis": ma,
                "angle": angle
            })
        else:
            print(f"Skipped: frame {frame_num}, class {class_id} — not enough points to fit an ellipse")



# Convert to DataFrame
df = pd.DataFrame(records)

# --------- PLOTTING ---------

def plot_position(df):
    plt.figure(figsize=(10, 5))
    for label in df['label'].unique():
        subset = df[df['label'] == label]
        plt.plot(subset['frame'], subset['cx'], label=f'{label} x', linestyle='--')
        plt.plot(subset['frame'], subset['cy'], label=f'{label} y')
    plt.xlabel("Frame")
    plt.ylabel("Position (pixels)")
    plt.title("X and Y Position of Ellipses")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_properties(df):
    fig, axs = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

    for label in df['label'].unique():
        subset = df[df['label'] == label]
        axs[0].plot(subset['frame'], subset['angle'], label=label)
        axs[1].plot(subset['frame'], subset['major_axis'], label=label)
        axs[2].plot(subset['frame'], subset['minor_axis'], label=label)

    axs[0].set_ylabel("Angle (deg)")
    axs[1].set_ylabel("Major Axis (px)")
    axs[2].set_ylabel("Minor Axis (px)")
    axs[2].set_xlabel("Frame")
    
    for ax in axs:
        ax.legend()
        ax.grid(True)

    plt.suptitle("Ellipse Orientation and Size")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

# --------- RUN ---------
if df.empty:
    print(" No valid ellipses were processed. Check if your TXT files have enough points (>=5) per polygon.")
else:
    print(" Ellipses processed:", len(df))
    plot_position(df)
    plot_properties(df)


