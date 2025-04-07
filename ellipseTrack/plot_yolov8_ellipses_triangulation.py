import os
import numpy as np
import matplotlib.pyplot as plt
import math
import re
from collections import defaultdict
from scipy.optimize import least_squares

def natural_sort_key(s):
    """Key function for natural sorting of filenames."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

# Constants for real-world conversion
WHEEL_DIAMETER = 28.0  # inches
PIXELS_PER_INCH = 100.0  # This needs calibration for your specific setup
BASELINE_DISTANCE = WHEEL_DIAMETER * math.pi  # Circumference as baseline (adjust as needed)

def triangulate_position(centers, baseline=BASELINE_DISTANCE):
    """
    Triangulate real-world positions using two ellipse centers as stereo pair.
    Assumes centers are from two cameras with known baseline distance.
    """
    if len(centers) != 2:
        return None
    
    # Convert pixel coordinates to normalized coordinates
    x1, y1 = centers[0]
    x2, y2 = centers[1]
    
    # Simple stereo triangulation (replace with your actual camera calibration)
    z = (baseline * PIXELS_PER_INCH) / (x1 - x2 + 1e-6)  # Avoid division by zero
    x = (x1 + x2) / 2 / PIXELS_PER_INCH
    y = (y1 + y2) / 2 / PIXELS_PER_INCH
    
    return x, y, z

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
        
        # Convert axes to inches
        major_axis_in = major_axis / PIXELS_PER_INCH
        minor_axis_in = minor_axis / PIXELS_PER_INCH
        
        ellipses.append({
            'class_id': class_id,
            'center': center,
            'center_in': (center[0]/PIXELS_PER_INCH, center[1]/PIXELS_PER_INCH),
            'major_axis': major_axis,
            'minor_axis': minor_axis,
            'major_axis_in': major_axis_in,
            'minor_axis_in': minor_axis_in,
            'angle': angle
        })
    
    return ellipses

def process_directory(directory_path, img_width=1.0, img_height=1.0):
    """Process all .txt files and collect ellipse data over time."""
    files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
    files.sort(key=natural_sort_key)
    
    tracking_data = defaultdict(lambda: {
        'x_pos': [], 'y_pos': [], 'x_pos_in': [], 'y_pos_in': [],
        'major_axes': [], 'minor_axes': [], 'major_axes_in': [], 'minor_axes_in': [],
        'angles': [], 'frames': [], 'real_pos': []
    })
    
    for frame_idx, filename in enumerate(files):
        file_path = os.path.join(directory_path, filename)
        ellipses = parse_yolov8_segmentation(file_path, img_width, img_height)
        
        # Store individual ellipse data
        for ellipse in ellipses:
            class_id = ellipse['class_id']
            tracking_data[class_id]['x_pos'].append(ellipse['center'][0])
            tracking_data[class_id]['y_pos'].append(ellipse['center'][1])
            tracking_data[class_id]['x_pos_in'].append(ellipse['center_in'][0])
            tracking_data[class_id]['y_pos_in'].append(ellipse['center_in'][1])
            tracking_data[class_id]['major_axes'].append(ellipse['major_axis'])
            tracking_data[class_id]['minor_axes'].append(ellipse['minor_axis'])
            tracking_data[class_id]['major_axes_in'].append(ellipse['major_axis_in'])
            tracking_data[class_id]['minor_axes_in'].append(ellipse['minor_axis_in'])
            tracking_data[class_id]['angles'].append(ellipse['angle'])
            tracking_data[class_id]['frames'].append(frame_idx)
        
        # Perform triangulation if we have exactly two ellipses (stereo pair)
        if len(ellipses) == 2:
            centers = [e['center'] for e in ellipses]
            real_pos = triangulate_position(centers)
            if real_pos:
                for i, ellipse in enumerate(ellipses):
                    tracking_data[ellipse['class_id']]['real_pos'].append(real_pos)
    
    return tracking_data

def plot_trajectories(tracking_data):
    """Plot position vs time and characteristics evolution."""
    plt.figure(figsize=(18, 12))
    colors = plt.cm.tab10.colors
    
    # Plot 1-2: Pixel Coordinates vs Time
    ax1 = plt.subplot(2, 3, 1)
    ax2 = plt.subplot(2, 3, 2)
    
    # Plot 3-4: Real-world Coordinates (inches)
    ax3 = plt.subplot(2, 3, 3)
    
    # Plot 5-6: Characteristics
    ax5 = plt.subplot(2, 3, 5)
    ax6 = plt.subplot(2, 3, 6)
    
    for class_id, data in tracking_data.items():
        color = colors[class_id % len(colors)]
        
        # Pixel coordinates
        ax1.plot(data['frames'], data['x_pos'], '-', color=color, label=f'Ellipse {class_id}')
        ax2.plot(data['frames'], data['y_pos'], '-', color=color, label=f'Ellipse {class_id}')
        
        # Real-world coordinates (if available)
        if data['real_pos']:
            real_x = [pos[0] for pos in data['real_pos']]
            real_y = [pos[1] for pos in data['real_pos']]
            real_z = [pos[2] for pos in data['real_pos']]
            ax3.plot(data['frames'][:len(real_x)], real_x, '-', color=color, label=f'X {class_id}')
            ax3.plot(data['frames'][:len(real_y)], real_y, '--', color=color, label=f'Y {class_id}')
            ax3.plot(data['frames'][:len(real_z)], real_z, ':', color=color, label=f'Z {class_id}')
        
        # Characteristics
        ax5.plot(data['frames'], data['major_axes_in'], '-', color=color, label=f'Major {class_id}')
        ax5.plot(data['frames'], data['minor_axes_in'], '--', color=color, label=f'Minor {class_id}')
        ax6.plot(data['frames'], data['angles'], '-', color=color, label=f'Angle {class_id}')
    
    # Configure plots
    ax1.set_title('X Position (pixels) vs Time')
    ax1.set_ylabel('X (pixels)')
    ax1.grid(True)
    ax1.legend()
    
    ax2.set_title('Y Position (pixels) vs Time')
    ax2.set_ylabel('Y (pixels)')
    ax2.grid(True)
    ax2.legend()
    
    ax3.set_title('Real-World Coordinates (inches)')
    ax3.set_ylabel('Distance (inches)')
    ax3.grid(True)
    ax3.legend()
    
    ax5.set_title('Axes Lengths (inches) vs Time')
    ax5.set_xlabel('Frame number')
    ax5.set_ylabel('Length (inches)')
    ax5.grid(True)
    ax5.legend()
    
    ax6.set_title('Angle vs Time')
    ax6.set_xlabel('Frame number')
    ax6.set_ylabel('Angle (degrees)')
    ax6.grid(True)
    ax6.legend()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Plot ellipse trajectories with real-world triangulation.')
    parser.add_argument('directory', type=str, help='Directory containing YOLOv8 .txt files')
    parser.add_argument('--width', type=float, default=1.0, help='Image width for coordinate scaling')
    parser.add_argument('--height', type=float, default=1.0, help='Image height for coordinate scaling')
    parser.add_argument('--pixels_per_inch', type=float, default=100.0, 
                       help='Calibration factor: pixels per inch in the image')
    
    args = parser.parse_args()
    
    # Update constants based on arguments
    PIXELS_PER_INCH = args.pixels_per_inch
    
    tracking_data = process_directory(args.directory, args.width, args.height)
    plot_trajectories(tracking_data)
