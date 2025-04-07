import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import math
import re

def natural_sort_key(s):
    """
    Key function for natural sorting of filenames.
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def parse_yolov8_segmentation(file_path, img_width=1.0, img_height=1.0):
    """
    Parse YOLOv8 segmentation data from a text file and extract ellipse parameters.
    Returns a list of ellipses (one for each object in the file).
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    ellipses = []
    for line in lines:
        parts = list(map(float, line.strip().split()))
        if len(parts) < 11:  # Need at least 5 points (5*2=10) + class_id
            continue
            
        class_id = int(parts[0])
        points = np.array(parts[1:]).reshape(-1, 2)
        
        # Convert normalized coordinates to absolute coordinates
        points[:, 0] *= img_width
        points[:, 1] *= img_height
        
        # Calculate ellipse parameters from the polygon points
        center = np.mean(points, axis=0)
        centered_points = points - center
        
        # Calculate covariance matrix
        cov = np.cov(centered_points.T)
        
        # Get eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eig(cov)
        
        # Calculate major and minor axes (2 * sqrt(eigenvalues))
        major_axis = 2 * math.sqrt(max(eigenvalues))
        minor_axis = 2 * math.sqrt(min(eigenvalues))
        
        # Calculate angle (in degrees)
        angle = math.degrees(math.atan2(eigenvectors[1, 0], eigenvectors[0, 0]))
        
        ellipses.append({
            'class_id': class_id,
            'center': center,
            'major_axis': major_axis,
            'minor_axis': minor_axis,
            'angle': angle
        })
    
    return ellipses

def process_directory(directory_path, img_width=1.0, img_height=1.0):
    """
    Process all .txt files in a directory and collect ellipse data over time.
    Returns a dictionary with tracking data for each ellipse class.
    """
    # Get sorted list of files
    files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
    files.sort(key=natural_sort_key)
    
    # Dictionary to store tracking data for each class
    tracking_data = {}
    
    for frame_idx, filename in enumerate(files):
        file_path = os.path.join(directory_path, filename)
        ellipses = parse_yolov8_segmentation(file_path, img_width, img_height)
        
        for ellipse in ellipses:
            class_id = ellipse['class_id']
            
            if class_id not in tracking_data:
                tracking_data[class_id] = {
                    'centers': [],
                    'major_axes': [],
                    'minor_axes': [],
                    'angles': [],
                    'frames': []
                }
            
            tracking_data[class_id]['centers'].append(ellipse['center'])
            tracking_data[class_id]['major_axes'].append(ellipse['major_axis'])
            tracking_data[class_id]['minor_axes'].append(ellipse['minor_axis'])
            tracking_data[class_id]['angles'].append(ellipse['angle'])
            tracking_data[class_id]['frames'].append(frame_idx)
    
    return tracking_data

def plot_trajectories(tracking_data):
    """
    Plot the trajectories of ellipse centers and their characteristics over time.
    Creates two side-by-side plots:
    1. Trajectory of centers
    2. Evolution of axes lengths and angles
    """
    plt.figure(figsize=(16, 6))
    
    # Define colors for different classes
    colors = plt.cm.tab10.colors
    
    # Plot 1: Trajectory of centers
    plt.subplot(1, 2, 1)
    for class_id, data in tracking_data.items():
        centers = np.array(data['centers'])
        color = colors[class_id % len(colors)]
        
        # Plot trajectory
        plt.plot(centers[:, 0], centers[:, 1], '.-', color=color, 
                label=f'Object {class_id}', markersize=8, linewidth=1.5)
        
        # Mark start and end points
        plt.plot(centers[0, 0], centers[0, 1], 'o', color=color, markersize=10)
        plt.plot(centers[-1, 0], centers[-1, 1], 's', color=color, markersize=10)
    
    plt.gca().invert_yaxis()  # YOLO format has origin at top-left
    plt.title('Trajectory of Ellipse Centers')
    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    plt.grid(True)
    plt.legend()
    plt.axis('equal')
    
    # Plot 2: Evolution of characteristics
    plt.subplot(1, 2, 2)
    for class_id, data in tracking_data.items():
        frames = np.array(data['frames'])
        color = colors[class_id % len(colors)]
        
        # Plot major and minor axes
        plt.plot(frames, data['major_axes'], '.-', color=color, 
                label=f'Object {class_id} (Major)', linewidth=1.5)
        plt.plot(frames, data['minor_axes'], '.:', color=color, 
                label=f'Object {class_id} (Minor)', linewidth=1.5)
        
        # Plot angle on secondary y-axis
        ax2 = plt.gca().twinx()
        ax2.plot(frames, data['angles'], '.--', color=color, 
                label=f'Object {class_id} (Angle)', linewidth=1.5, alpha=0.7)
    
    plt.title('Evolution of Ellipse Characteristics')
    plt.xlabel('Frame number')
    plt.ylabel('Axis length')
    ax2.set_ylabel('Angle (degrees)')
    
    # Combine legends from both axes
    lines1, labels1 = plt.gca().get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    plt.gca().legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Plot ellipse trajectories from YOLOv8 segmentation files.')
    parser.add_argument('directory', type=str, help='Directory containing YOLOv8 .txt files')
    parser.add_argument('--width', type=float, default=1.0, help='Image width for coordinate scaling')
    parser.add_argument('--height', type=float, default=1.0, help='Image height for coordinate scaling')
    
    args = parser.parse_args()
    
    tracking_data = process_directory(args.directory, args.width, args.height)
    plot_trajectories(tracking_data)
