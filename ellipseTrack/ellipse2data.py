import os
import numpy as np
import matplotlib.pyplot as plt
import math
import argparse
import re
from collections import defaultdict
from scipy.signal import butter, filtfilt

plt.rcParams['figure.constrained_layout.use'] = True
plt.rcParams.update({'font.size': 16})


def readEllipse(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    ellipses = []

    for line in lines:
        parts = list(map(float, line.strip().split()))

        class_id = int(parts[0])
        points = np.array(parts[1:]).reshape(-1, 2)
        center = np.mean(points, axis=0)
        centered_points = points - center
        cov = np.cov(centered_points.T)
        eigenvalues, eigenvectors = np.linalg.eig(cov)
        major_axis = 2 * math.sqrt(max(eigenvalues))
        minor_axis = 2 * math.sqrt(min(eigenvalues))

        ellipses.append({
            'class_id': class_id,
            'center': center,
            'major_axis': major_axis,
            'minor_axis': minor_axis,
        })

        return ellipses
    
def process_directory(directory_path):
    """Process all .txt files in directory."""
    files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
    files.sort()#key=natural_sort_key)
    
    tracking_data = defaultdict(lambda: {
        'x_pos': [], 'y_pos': [], 'major_axes': [], 'minor_axes': [], 'frames': []
    })
    
    for frame_idx, filename in enumerate(files):
        file_path = os.path.join(directory_path, filename)
        for ellipse in readEllipse(file_path):
            class_id = ellipse['class_id']
            tracking_data[class_id]['x_pos'].append(ellipse['center'][0])
            tracking_data[class_id]['y_pos'].append(ellipse['center'][1])
            tracking_data[class_id]['major_axes'].append(ellipse['major_axis'])
            tracking_data[class_id]['minor_axes'].append(ellipse['minor_axis'])
            tracking_data[class_id]['frames'].append(frame_idx)
    
    return tracking_data



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot ellipse data with customizable options.')
    parser.add_argument('directory', type=str, help='Directory containing YOLOv8 .txt files')
    parser.add_argument('--cutoff', type=float, default=2.0, help='Lowpass filter cutoff frequency')
    parser.add_argument('--fs', type=float, default=30.0, help='Sampling frequency')
    parser.add_argument('--raw', action='store_true', help='Show raw data along with filtered data')
    parser.add_argument('--absolute', action='store_true', help='Show absolute differences (default)')
    parser.add_argument('--signed', action='store_true', help='Show signed differences instead of absolute')
    
    args = parser.parse_args()
    
    # Handle mutual exclusion for difference type
    if args.signed:
        absolute_diff = False
    else:
        absolute_diff = True  # Default to absolute differences
    
    tracking_data = process_directory(args.directory)
    # filtered_data = apply_filters(tracking_data, args.cutoff, args.fs)
    plot_data(tracking_data, filtered_data, show_raw=args.raw, absolute_diff=absolute_diff)