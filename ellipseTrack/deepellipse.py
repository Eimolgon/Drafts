import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import math

def parse_yolov8_segmentation(file_path, img_width=1.0, img_height=1.0):
    """
    Parse YOLOv8 segmentation data from a text file and extract ellipse parameters.
    YOLOv8 segmentation format: class x1 y1 x2 y2 ... xn yn (normalized coordinates)
    For ellipses, we assume the points represent a polygon approximation of the ellipse.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    ellipses = []
    for line in lines:
        parts = list(map(float, line.strip().split()))
        class_id = int(parts[0])
        points = np.array(parts[1:]).reshape(-1, 2)
        
        # Convert normalized coordinates to absolute coordinates
        points[:, 0] *= img_width
        points[:, 1] *= img_height
        
        # Calculate ellipse parameters from the polygon points
        if len(points) >= 5:  # Need at least 5 points to fit an ellipse
            center = np.mean(points, axis=0)
            centered_points = points - center
            
            # Calculate covariance matrix
            cov = np.cov(centered_points.T)
            
            # Get eigenvalues and eigenvectors
            eigenvalues, eigenvectors = np.linalg.eig(cov)
            
            # Calculate major and minor axes (2 * sqrt(eigenvalues))
            # We multiply by 2 because eigenvalues are variances of the coordinates
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

def plot_ellipses(ellipses, title="Ellipses Visualization"):
    """
    Plot ellipses with their centers, axes, and angles.
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Set equal aspect ratio
    ax.set_aspect('equal')
    
    # Set axis limits (assuming normalized coordinates)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.invert_yaxis()  # YOLO format has origin at top-left
    
    colors = ['red', 'blue', 'green', 'purple', 'orange']  # Different colors for different classes
    
    for ellipse in ellipses:
        color = colors[ellipse['class_id'] % len(colors)]
        
        # Create and add ellipse patch
        ell = Ellipse(xy=ellipse['center'], 
                      width=ellipse['major_axis'], 
                      height=ellipse['minor_axis'],
                      angle=ellipse['angle'],
                      edgecolor=color,
                      facecolor='none',
                      linewidth=2,
                      alpha=0.7)
        ax.add_patch(ell)
        
        # Plot center
        ax.plot(ellipse['center'][0], ellipse['center'][1], 'o', color=color, markersize=8)
        
        # Plot major and minor axes
        angle_rad = math.radians(ellipse['angle'])
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        
        # Major axis line
        major_end1 = ellipse['center'] + 0.5 * ellipse['major_axis'] * np.array([cos_a, sin_a])
        major_end2 = ellipse['center'] - 0.5 * ellipse['major_axis'] * np.array([cos_a, sin_a])
        ax.plot([major_end1[0], major_end2[0]], [major_end1[1], major_end2[1]], '--', color=color, linewidth=1.5)
        
        # Minor axis line
        minor_end1 = ellipse['center'] + 0.5 * ellipse['minor_axis'] * np.array([-sin_a, cos_a])
        minor_end2 = ellipse['center'] - 0.5 * ellipse['minor_axis'] * np.array([-sin_a, cos_a])
        ax.plot([minor_end1[0], minor_end2[0]], [minor_end1[1], minor_end2[1]], ':', color=color, linewidth=1.5)
        
        # Add angle text near the center
        angle_text = f"{ellipse['angle']:.1f}°"
        ax.text(ellipse['center'][0] + 0.05, ellipse['center'][1] - 0.05, angle_text, 
                color=color, fontsize=10, ha='left', va='center')
    
    ax.set_title(title)
    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')
    plt.grid(True)
    plt.show()

def process_directory(directory_path, img_width=1.0, img_height=1.0):
    """
    Process all .txt files in a directory and plot the ellipses.
    """
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory_path, filename)
            ellipses = parse_yolov8_segmentation(file_path, img_width, img_height)
            
            if ellipses:
                plot_ellipses(ellipses, title=f"Ellipses from {filename}")
            else:
                print(f"No ellipses found in {filename}")

# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Plot ellipses from YOLOv8 segmentation files.')
    parser.add_argument('directory', type=str, help='Directory containing YOLOv8 .txt files')
    parser.add_argument('--width', type=float, default=1.0, help='Image width for coordinate scaling')
    parser.add_argument('--height', type=float, default=1.0, help='Image height for coordinate scaling')
    
    args = parser.parse_args()
    
    process_directory(args.directory, args.width, args.height)
