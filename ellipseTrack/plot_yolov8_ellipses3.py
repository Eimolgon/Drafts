import os
import numpy as np
import matplotlib.pyplot as plt
import math
import re
from collections import defaultdict

def natural_sort_key(s):
    """Key function for natural sorting of filenames."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def parse_yolov8_segmentation(file_path, img_width=1.0, img_height=1.0):
    """Parse YOLOv8 segmentation data and extract ellipse parameters."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    ellipses = []
    for line in lines:
        parts = list(map(float, line.strip().split()))
        if len(parts) < 11:  # Need at least 5 points (5*2=10) + class_id
            continue
            
        class_id = int(parts[0])
        if class_id == 0:
            class_name = 'Front wheel'
        elif class_id == 1:
            class_name = 'Rear wheel'
        points = np.array(parts[1:]).reshape(-1, 2)
        
        # Convert normalized coordinates to absolute coordinates
        points[:, 0] *= img_width
        points[:, 1] *= img_height
        
        # Calculate ellipse parameters
        center = np.mean(points, axis=0)
        centered_points = points - center
        cov = np.cov(centered_points.T)
        eigenvalues, eigenvectors = np.linalg.eig(cov)
        major_axis = 2 * math.sqrt(max(eigenvalues))
        minor_axis = 2 * math.sqrt(min(eigenvalues))
        angle = math.degrees(math.atan2(eigenvectors[1, 0], eigenvectors[0, 0]))
        
        ellipses.append({
            'class_id': class_id,
            'class_name': class_name,
            'center': center,
            'major_axis': major_axis,
            'minor_axis': minor_axis,
            'angle': angle
        })
    
    return ellipses

def process_directory(directory_path, img_width=1.0, img_height=1.0):
    """Process all .txt files and collect ellipse data over time."""
    files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
    files.sort(key=natural_sort_key)
    
    tracking_data = defaultdict(lambda: {
        'x_pos': [], 'y_pos': [], 'major_axes': [], 'minor_axes': [], 'angles': [], 'frames': []
    })
    
    for frame_idx, filename in enumerate(files):
        file_path = os.path.join(directory_path, filename)
        for ellipse in parse_yolov8_segmentation(file_path, img_width, img_height):
            class_id = ellipse['class_id']
            tracking_data[class_id]['x_pos'].append(ellipse['center'][0])
            tracking_data[class_id]['y_pos'].append(ellipse['center'][1])
            tracking_data[class_id]['major_axes'].append(ellipse['major_axis'])
            tracking_data[class_id]['minor_axes'].append(ellipse['minor_axis'])
            tracking_data[class_id]['angles'].append(ellipse['angle'])
            tracking_data[class_id]['frames'].append(frame_idx)
    
    return tracking_data

def plot_trajectories(tracking_data):
    """Plot position vs time and characteristics evolution."""
    plt.figure(figsize=(15, 10))
    colors = plt.cm.tab10.colors
    
    # Plot 1: X Position vs Time
    ax1 = plt.subplot(2, 2, 1)
    for class_id, data in tracking_data.items():
        if class_id == 0:
            class_name = 'Front wheel'
        elif class_id == 1:
            class_name = 'Rear wheel'
        color = colors[class_id % len(colors)]
        ax1.plot(data['frames'], data['x_pos'], '-', color=color, 
                label=f'{class_name}')
    ax1.set_title('X Position vs Time')
    ax1.set_xlabel('Frame number')
    ax1.set_ylabel('X coordinate')
    ax1.grid(True)
    ax1.legend()
    
    # Plot 2: Y Position vs Time
    ax2 = plt.subplot(2, 2, 2)
    for class_id, data in tracking_data.items(): 
        if class_id == 0:
            class_name = 'Front wheel'
        elif class_id == 1:
            class_name = 'Rear wheel'
        color = colors[class_id % len(colors)]
        ax2.plot(data['frames'], data['y_pos'], '-', color=color, 
                label=f'{class_name}')
    ax2.set_title('Y Position vs Time')
    ax2.set_xlabel('Frame number')
    ax2.set_ylabel('Y coordinate')
    ax2.grid(True)
    ax2.legend()
    
    # Plot 3: Axes Lengths vs Time
    ax3 = plt.subplot(2, 2, 3)
    for class_id, data in tracking_data.items():
        color = colors[class_id % len(colors)]
        ax3.plot(data['frames'], data['major_axes'], '-', color=color, 
                label=f'Major Axis {class_name}')
        ax3.plot(data['frames'], data['minor_axes'], '--', color=color,
                label=f'Minor Axis {class_name}')
    ax3.set_title('Axes Lengths vs Time')
    ax3.set_xlabel('Frame number')
    ax3.set_ylabel('Length')
    ax3.grid(True)
    ax3.legend()
    
    # Plot 4: Angle vs Time
    ax4 = plt.subplot(2, 2, 4)
    for class_id, data in tracking_data.items():
        color = colors[class_id % len(colors)]
        ax4.plot(data['frames'], data['angles'], '-', color=color, 
                label=f'Angle {class_name}')
    ax4.set_title('Angle vs Time')
    ax4.set_xlabel('Frame number')
    ax4.set_ylabel('Angle (degrees)')
    ax4.grid(True)
    ax4.legend()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Plot ellipse positions and characteristics over time.')
    parser.add_argument('directory', type=str, help='Directory containing YOLOv8 .txt files')
    parser.add_argument('--width', type=float, default=1.0, help='Image width for coordinate scaling')
    parser.add_argument('--height', type=float, default=1.0, help='Image height for coordinate scaling')
    
    args = parser.parse_args()
    
    tracking_data = process_directory(args.directory, args.width, args.height)
    plot_trajectories(tracking_data)
