import os
import numpy as np
import matplotlib.pyplot as plt
import math
import argparse
import re
import pandas as pd
from collections import defaultdict
from scipy.signal import butter, filtfilt

plt.rcParams['figure.constrained_layout.use'] = True
plt.rcParams.update({'font.size': 16})


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


def apply_filters(tracking_data, cutoff=2.0, fs=30.0):
    """Apply lowpass filters to all tracking data."""
    filtered_data = {}
    for class_id, data in tracking_data.items():
        filtered = {
            'x_pos': lowpass_filter(data['x_pos'], cutoff, fs),
            'y_pos': lowpass_filter(data['y_pos'], cutoff, fs),
            'major_axes': lowpass_filter(data['major_axes'], cutoff, fs),
            'minor_axes': lowpass_filter(data['minor_axes'], cutoff, fs),
            'frames': data['frames']
        }
        filtered_data[class_id] = filtered
    return filtered_data


def plot_data(tracking_data, filtered_data, show_raw=False, absolute_diff=True):
    """Plot data with specified options."""
    plt.figure(figsize=(18, 12))  # Adjusted figure size
    
    # Define color scheme
    ellipse_colors = ['turquoise', 'red']
    diff_colors = ['green', 'orange']
    raw_alpha = 0.3 if show_raw else 0
    
    # Calculate differences
    # diff_metrics = calculate_differences(filtered_data, absolute_diff)
    
    # Plot X Position
    ax1 = plt.subplot(2, 3, 1)
    for class_id, data in tracking_data.items():
        if class_id == 0:
            class_name = 'Front'
        elif class_id == 1:
            class_name = 'Rear'

        if show_raw:
            ax1.plot(data['frames'], data['x_pos'], '-', color=ellipse_colors[class_id], 
                    alpha=raw_alpha, label=f'{class_name} wheel raw')
        ax1.plot(filtered_data[class_id]['frames'], filtered_data[class_id]['x_pos'], '-', 
                color=ellipse_colors[class_id], linewidth=2, label=f'{class_name} wheel filtered')
    ax1.set_title('$x$ Position', fontweight='bold')
    ax1.set_ylabel('$x$ position (pixels)')#, fontsize = 16)
    ax1.legend()
    ax1.grid(True)
    
    # Plot Y Position (inverted for user-friendly view)
    ax2 = plt.subplot(2, 3, 2)
    for class_id, data in tracking_data.items():
        if show_raw:
            ax2.plot(data['frames'], data['y_pos'], '-', color=ellipse_colors[class_id], 
                    alpha=raw_alpha, label=f'{class_name} wheel Y raw')
        ax2.plot(filtered_data[class_id]['frames'], filtered_data[class_id]['y_pos'], '-', 
                color=ellipse_colors[class_id], linewidth=2, label=f'{class_name} wheel filtered')
    ax2.set_title('$y$ Position', fontweight='bold')
    ax2.set_ylabel('$y$ position (pixels)')
    ax2.invert_yaxis()
    ax2.grid(True)
    
    # Plot Major/Minor Axis Ratio
    ax3 = plt.subplot(2, 3, 3)
    for class_id, data in tracking_data.items():

        if class_id == 0:
            class_name = 'Front'
        elif class_id == 1:
            class_name = 'Rear'

        # Calculate ratio
        if show_raw:
            ratio_raw = np.array(data['major_axes']) / np.array(data['minor_axes'])
            ax3.plot(data['frames'], ratio_raw, '-', color=ellipse_colors[class_id], 
                    alpha=raw_alpha, label=f'{class_name} wheel ellipse ratio')
        
        ratio_filtered = np.array(filtered_data[class_id]['major_axes']) / np.array(filtered_data[class_id]['minor_axes'])
        ax3.plot(filtered_data[class_id]['frames'], ratio_filtered, '-', 
                color=ellipse_colors[class_id], linewidth=2, label=f'{class_name} wheel ellipse ratio')
    ax3.set_title('Major/Minor Axis Ratio', fontweight='bold')
    ax3.set_ylabel('Ratio (major/minor)')
    ax3.axhline(1.0, color='gray', linestyle='--', alpha=0.5)
    ax3.legend()
    ax3.grid(True)
    
    # # Plot Angle
    # ax4 = plt.subplot(2, 3, 6)
    # for class_id, data in tracking_data.items():
    #     if show_raw:
    #         ax4.plot(data['frames'], data['angles'], '-', color=ellipse_colors[class_id], 
    #                 alpha=raw_alpha, label=f'{class_name} wheel')
    #     ax4.plot(filtered_data[class_id]['frames'], filtered_data[class_id]['angles'], '-', 
    #             color=ellipse_colors[class_id], linewidth=2, label=f'{class_name} wheel')
    # ax4.set_title('Angle', fontweight='bold')
    # ax4.set_xlabel('Frame number')
    # ax4.set_ylabel('Angle (degrees)')
    # ax4.grid(True)
    
    # # Plot X Differences (NEW separate plot)
    # ax5 = plt.subplot(2, 3, 4)
    # if diff_metrics:
    #     ax5.plot(diff_metrics['frames'], diff_metrics['x_difference'], '-', 
    #             color=diff_colors[0], label='$x$ Difference')
        
    #     diff_type = 'Absolute' if absolute_diff else 'Signed'
    #     ax5.set_title(f'$x$ Distance', fontweight='bold')
    #     ax5.set_xlabel('Frame number')
    #     ax5.set_ylabel(f'$x$ Distance (pixels)')
    #     ax5.legend()
    #     ax5.grid(True)
        
    #     if not absolute_diff:
    #         ax5.axhline(0, color='black', linestyle='--', alpha=0.5)
    # else:
    #     ax5.text(0.5, 0.5, 'Not enough ellipses for difference calculation', 
    #             ha='center', va='center')
    #     ax5.set_title('X Differences (Not Available)')
    
    # # Plot Y Differences (NEW separate plot)
    # ax6 = plt.subplot(2, 3, 5)
    # if diff_metrics:
    #     ax6.plot(diff_metrics['frames'], diff_metrics['y_difference'], '-', 
    #             color=diff_colors[1], label='Y Difference')
        
    #     diff_type = 'Absolute' if absolute_diff else 'Signed'
    #     ax6.set_title(f'$y$ Distance', fontweight='bold')
    #     ax6.set_xlabel('Frame number')
    #     ax6.set_ylabel(f'$y$ Distance (pixels)')
    #     ax6.legend()
    #     ax6.grid(True)
        
    #     if not absolute_diff:
    #         ax6.axhline(0, color='black', linestyle='--', alpha=0.5)
    # else:
    #     ax6.text(0.5, 0.5, 'Not enough ellipses for difference calculation', 
    #             ha='center', va='center')
    #     ax6.set_title('Y Differences (Not Available)')
    
    plt.tight_layout()
    plt.show()


def create_4column_csv(tracking_data, filtered_data, output_file):
    '''Create 4-column CSV with Feature 1 time, Feature 1 [x,y], Feature 2 time, Feature 2 [x,y]'''
    
    if len(tracking_data) < 2:
        print("Need at least 2 ellipses to create 4-column output")
        return
    
    # Get all available frames from both ellipses
    all_frames = set()
    for class_id in [0, 1]:
        if class_id in tracking_data:
            all_frames.update(tracking_data[class_id]['frames'])
    
    all_frames = sorted(all_frames)
    
    # Create dictionaries for quick lookup by frame
    ellipse0_data = {}
    ellipse1_data = {}
    
    # Populate ellipse 0 data
    if 0 in tracking_data:
        for i, frame in enumerate(tracking_data[0]['frames']):
            ellipse0_data[frame] = {
                'x': tracking_data[0]['x_pos'][i],
                'y': tracking_data[0]['y_pos'][i]
            }
    
    # Populate ellipse 1 data
    if 1 in tracking_data:
        for i, frame in enumerate(tracking_data[1]['frames']):
            ellipse1_data[frame] = {
                'x': tracking_data[1]['x_pos'][i],
                'y': tracking_data[1]['y_pos'][i]
            }
    
    # Create the 4-column data structure
    data = []
    for frame in all_frames:
        # Get ellipse 0 data or use NaN if missing
        if frame in ellipse0_data:
            ellipse0_str = f"[{ellipse0_data[frame]['x']:.2f}, {ellipse0_data[frame]['y']:.2f}]"
        else:
            ellipse0_str = "[nan, nan]"
        
        # Get ellipse 1 data or use NaN if missing
        if frame in ellipse1_data:
            ellipse1_str = f"[{ellipse1_data[frame]['x']:.2f}, {ellipse1_data[frame]['y']:.2f}]"
        else:
            ellipse1_str = "[nan, nan]"
        
        row = [
            frame,          # Feature 1 time
            ellipse0_str,   # Feature 1 [x,y]
            frame,          # Feature 2 time (same timestamp)
            ellipse1_str    # Feature 2 [x,y]
        ]
        data.append(row)
    
    # Create DataFrame and save as CSV
    df = pd.DataFrame(data, columns=[
        'Feature1_time', 
        'Feature1_[x,y]', 
        'Feature2_time', 
        'Feature2_[x,y]'
    ])
    
    df.to_csv(output_file, index=False)
    print(f"4-column CSV saved to: {output_file}")
    print(f"Total rows: {len(df)}")
    print(f"Columns: {', '.join(df.columns)}")
    print(f"Frames with ellipse 0 data: {len(ellipse0_data)}")
    print(f"Frames with ellipse 1 data: {len(ellipse1_data)}")
    print(f"Total unique frames: {len(all_frames)}")
    print("\nFirst 10 rows:")
    print(df.head(10))
    
    return df



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot ellipse data with customizable options.')
    parser.add_argument('directory', type=str, help='Directory containing YOLOv8 .txt files')
    parser.add_argument('--cutoff', type=float, default=2.0, help='Lowpass filter cutoff frequency')
    parser.add_argument('--fs', type=float, default=30.0, help='Sampling frequency')
    parser.add_argument('--raw', action='store_true', help='Show raw data along with filtered data')
    parser.add_argument('--absolute', action='store_true', help='Show absolute differences (default)')
    parser.add_argument('--signed', action='store_true', help='Show signed differences instead of absolute')
    parser.add_argument('--output', type=str, default='ellipse_features.csv', help='Output CSV filename')
    
    args = parser.parse_args()
    
    # Handle mutual exclusion for difference type
    if args.signed:
        absolute_diff = False
    else:
        absolute_diff = True  # Default to absolute differences
    
    tracking_data = process_directory(args.directory)
    filtered_data = apply_filters(tracking_data, args.cutoff, args.fs)
    create_4column_csv(tracking_data, filtered_data, args.output)

    plot_data(tracking_data, filtered_data, show_raw=args.raw, absolute_diff=absolute_diff)