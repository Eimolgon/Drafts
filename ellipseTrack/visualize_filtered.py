import os
import numpy as np
import matplotlib.pyplot as plt
import math
import re
from collections import defaultdict
from scipy.signal import butter, filtfilt

def butter_lowpass(cutoff, fs, order=5):
    """Design a Butterworth lowpass filter."""
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def lowpass_filter(data, cutoff=2.0, fs=30.0, order=5):
    """Apply lowpass filter to data."""
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def natural_sort_key(s):
    """Natural sorting for filenames."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def parse_yolov8_segmentation(file_path):
    """Parse YOLOv8 segmentation data."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    ellipses = []
    for line in lines:
        parts = list(map(float, line.strip().split()))
        if len(parts) < 11:  # Need at least 5 points
            continue
            
        class_id = int(parts[0])
        points = np.array(parts[1:]).reshape(-1, 2)
        center = np.mean(points, axis=0)
        centered_points = points - center
        cov = np.cov(centered_points.T)
        eigenvalues, eigenvectors = np.linalg.eig(cov)
        major_axis = 2 * math.sqrt(max(eigenvalues))
        minor_axis = 2 * math.sqrt(min(eigenvalues))
        angle = math.degrees(math.atan2(eigenvectors[1, 0], eigenvectors[0, 0]))
        
        ellipses.append({
            'class_id': class_id,
            'center': center,
            'major_axis': major_axis,
            'minor_axis': minor_axis,
            'angle': angle
        })
    
    return ellipses

def process_directory(directory_path):
    """Process all .txt files in directory."""
    files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
    files.sort(key=natural_sort_key)
    
    tracking_data = defaultdict(lambda: {
        'x_pos': [], 'y_pos': [], 'major_axes': [], 'minor_axes': [], 'angles': [], 'frames': []
    })
    
    for frame_idx, filename in enumerate(files):
        file_path = os.path.join(directory_path, filename)
        for ellipse in parse_yolov8_segmentation(file_path):
            class_id = ellipse['class_id']
            tracking_data[class_id]['x_pos'].append(ellipse['center'][0])
            tracking_data[class_id]['y_pos'].append(ellipse['center'][1])
            tracking_data[class_id]['major_axes'].append(ellipse['major_axis'])
            tracking_data[class_id]['minor_axes'].append(ellipse['minor_axis'])
            tracking_data[class_id]['angles'].append(ellipse['angle'])
            tracking_data[class_id]['frames'].append(frame_idx)
    
    return tracking_data

def apply_filters(tracking_data, cutoff=2.0, fs=30.0):
    """Apply lowpass filters to all tracking data."""
    filtered_data = {}
    for class_id, data in tracking_data.items():
        filtered = {
            'x_pos': lowpass_filter(data['x_pos'], cutoff, fs),
            'y_pos': lowpass_filter(data['y_pos'], cutoff, fs),
            'major_axes': lowpass_filter(data['major_axes'], cutoff, fs),
            'minor_axes': lowpass_filter(data['minor_axes'], cutoff, fs),
            'angles': lowpass_filter(data['angles'], cutoff, fs),
            'frames': data['frames']
        }
        filtered_data[class_id] = filtered
    return filtered_data

def plot_comparison(tracking_data, filtered_data):
    """Plot raw and filtered data comparison."""
    plt.figure(figsize=(15, 10))
    colors = plt.cm.tab10.colors
    
    # Plot X Position
    ax1 = plt.subplot(2, 2, 1)
    for class_id, data in tracking_data.items():
        color = colors[class_id % len(colors)]
        ax1.plot(data['frames'], data['x_pos'], '-', color=color, alpha=0.5, label=f'Raw {class_id}')
        ax1.plot(filtered_data[class_id]['frames'], filtered_data[class_id]['x_pos'], '-', 
                color=color, linewidth=2, label=f'Filtered {class_id}')
    ax1.set_title('X Position Comparison')
    ax1.legend()
    
    # Plot Y Position
    ax2 = plt.subplot(2, 2, 2)
    for class_id, data in tracking_data.items():
        color = colors[class_id % len(colors)]
        ax2.plot(data['frames'], data['y_pos'], '-', color=color, alpha=0.5)
        ax2.plot(filtered_data[class_id]['frames'], filtered_data[class_id]['y_pos'], '-', 
                color=color, linewidth=2)
    ax2.set_title('Y Position Comparison')
    
    # Plot Major Axis
    ax3 = plt.subplot(2, 2, 3)
    for class_id, data in tracking_data.items():
        color = colors[class_id % len(colors)]
        ax3.plot(data['frames'], data['major_axes'], '-', color=color, alpha=0.5)
        ax3.plot(filtered_data[class_id]['frames'], filtered_data[class_id]['major_axes'], '-', 
                color=color, linewidth=2)
    ax3.set_title('Major Axis Comparison')
    
    # Plot Angle
    ax4 = plt.subplot(2, 2, 4)
    for class_id, data in tracking_data.items():
        color = colors[class_id % len(colors)]
        ax4.plot(data['frames'], data['angles'], '-', color=color, alpha=0.5)
        ax4.plot(filtered_data[class_id]['frames'], filtered_data[class_id]['angles'], '-', 
                color=color, linewidth=2)
    ax4.set_title('Angle Comparison')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Plot ellipse data with lowpass filtering.')
    parser.add_argument('directory', type=str, help='Directory containing YOLOv8 .txt files')
    parser.add_argument('--cutoff', type=float, default=2.0, help='Lowpass filter cutoff frequency')
    parser.add_argument('--fs', type=float, default=30.0, help='Sampling frequency')
    
    args = parser.parse_args()
    
    tracking_data = process_directory(args.directory)
    filtered_data = apply_filters(tracking_data, args.cutoff, args.fs)
    plot_comparison(tracking_data, filtered_data)
