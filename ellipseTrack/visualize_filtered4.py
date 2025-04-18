import os
import numpy as np
import matplotlib.pyplot as plt
import math
import re
from collections import defaultdict
from scipy.signal import butter, filtfilt
import argparse

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

def calculate_differences(filtered_data, absolute=True):
    """Calculate differences between both ellipses."""
    if len(filtered_data) < 2:
        return None
    
    # Get common frame range
    min_frames = min(len(filtered_data[0]['x_pos']), len(filtered_data[1]['x_pos']))
    frames = np.arange(min_frames)
    
    # Calculate differences
    x_diff = np.array(filtered_data[0]['x_pos'][:min_frames]) - np.array(filtered_data[1]['x_pos'][:min_frames])
    y_diff = np.array(filtered_data[0]['y_pos'][:min_frames]) - np.array(filtered_data[1]['y_pos'][:min_frames])
    
    if absolute:
        x_diff = np.abs(x_diff)
        y_diff = np.abs(y_diff)
    
    return {
        'x_difference': x_diff,
        'y_difference': y_diff,
        'frames': frames
    }

def plot_data(tracking_data, filtered_data, show_raw=False, absolute_diff=True):
    """Plot data with specified options."""
    plt.figure(figsize=(15, 12))
    
    # Define color scheme
    ellipse_colors = ['blue', 'orange']
    diff_colors = ['green', 'red']
    raw_alpha = 0.3 if show_raw else 0
    
    # Calculate differences
    diff_metrics = calculate_differences(filtered_data, absolute_diff)
    
    # Plot X Position
    ax1 = plt.subplot(3, 2, 1)
    for class_id, data in tracking_data.items():
        if show_raw:
            ax1.plot(data['frames'], data['x_pos'], '-', color=ellipse_colors[class_id], 
                    alpha=raw_alpha, label=f'Raw Ellipse {class_id} X')
        ax1.plot(filtered_data[class_id]['frames'], filtered_data[class_id]['x_pos'], '-', 
                color=ellipse_colors[class_id], linewidth=2, label=f'Filtered Ellipse {class_id} X')
    ax1.set_title('X Position')
    ax1.set_ylabel('X position (pixels)')
    ax1.legend()
    ax1.grid(True)
    
    # Plot Y Position (inverted)
    ax2 = plt.subplot(3, 2, 2)
    for class_id, data in tracking_data.items():
        if show_raw:
            ax2.plot(data['frames'], data['y_pos'], '-', color=ellipse_colors[class_id], 
                    alpha=raw_alpha, label=f'Raw Ellipse {class_id} Y')
        ax2.plot(filtered_data[class_id]['frames'], filtered_data[class_id]['y_pos'], '-', 
                color=ellipse_colors[class_id], linewidth=2, label=f'Filtered Ellipse {class_id} Y')
    ax2.set_title('Y Position (Inverted)')
    ax2.set_ylabel('Y position (pixels)')
    ax2.invert_yaxis()
    ax2.grid(True)
    
    # Plot Major Axis
    ax3 = plt.subplot(3, 2, 3)
    for class_id, data in tracking_data.items():
        if show_raw:
            ax3.plot(data['frames'], data['major_axes'], '-', color=ellipse_colors[class_id], 
                    alpha=raw_alpha, label=f'Raw Ellipse {class_id}')
        ax3.plot(filtered_data[class_id]['frames'], filtered_data[class_id]['major_axes'], '-', 
                color=ellipse_colors[class_id], linewidth=2, label=f'Filtered Ellipse {class_id}')
    ax3.set_title('Major Axis')
    ax3.set_ylabel('Major axis (pixels)')
    ax3.grid(True)
    
    # Plot Angle
    ax4 = plt.subplot(3, 2, 4)
    for class_id, data in tracking_data.items():
        if show_raw:
            ax4.plot(data['frames'], data['angles'], '-', color=ellipse_colors[class_id], 
                    alpha=raw_alpha, label=f'Raw Ellipse {class_id}')
        ax4.plot(filtered_data[class_id]['frames'], filtered_data[class_id]['angles'], '-', 
                color=ellipse_colors[class_id], linewidth=2, label=f'Filtered Ellipse {class_id}')
    ax4.set_title('Angle')
    ax4.set_ylabel('Angle (degrees)')
    ax4.grid(True)
    
    # Plot Differences
    ax5 = plt.subplot(3, 2, (5,6))
    if diff_metrics:
        ax5.plot(diff_metrics['frames'], diff_metrics['x_difference'], '-', 
                color=diff_colors[0], label='X Difference')
        ax5.plot(diff_metrics['frames'], diff_metrics['y_difference'], '-', 
                color=diff_colors[1], label='Y Difference')
        
        diff_type = 'Absolute' if absolute_diff else 'Signed'
        ax5.set_title(f'{diff_type} Differences Between Ellipses')
        ax5.set_xlabel('Frame number')
        ax5.set_ylabel(f'{diff_type} Difference (pixels)')
        ax5.legend()
        ax5.grid(True)
        
        # Add zero reference line for signed differences
        if not absolute_diff:
            ax5.axhline(0, color='black', linestyle='--', alpha=0.5)
    else:
        ax5.text(0.5, 0.5, 'Not enough ellipses for difference calculation', 
                ha='center', va='center')
        ax5.set_title('Differences (Not Available)')
    
    plt.tight_layout()
    plt.show()

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
    filtered_data = apply_filters(tracking_data, args.cutoff, args.fs)
    plot_data(tracking_data, filtered_data, show_raw=args.raw, absolute_diff=absolute_diff)
