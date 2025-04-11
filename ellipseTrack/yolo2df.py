import os
import numpy as np
import pandas as pd
import math
import re
from collections import defaultdict

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
            'center_x': center[0],
            'center_y': center[1],
            'major_axis': major_axis,
            'minor_axis': minor_axis,
            'angle': angle,
            'aspect_ratio': major_axis / (minor_axis + 1e-6),
            'area': math.pi * major_axis * minor_axis / 4
        })
    
    return ellipses

def process_directory(directory_path):
    """Process all .txt files in directory."""
    files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
    files.sort(key=natural_sort_key)
    
    all_data = []
    for frame_idx, filename in enumerate(files):
        file_path = os.path.join(directory_path, filename)
        
        for ellipse in parse_yolov8_segmentation(file_path):
            record = {
                'frame_id': frame_idx,
                **ellipse
            }
            all_data.append(record)
    
    return pd.DataFrame(all_data)

def save_dataset(df, output_file, csv_only=False):
    """Save dataset to file."""
    if csv_only:
        # Save only as CSV
        csv_file = output_file if output_file.endswith('.csv') else output_file + '.csv'
        df.to_csv(csv_file, index=False)
        print(f"Dataset saved to: {csv_file}")
    else:
        # Original behavior with multiple formats
        csv_file = os.path.splitext(output_file)[0] + '.csv'
        pq_file = os.path.splitext(output_file)[0] + '.parquet'
        json_file = os.path.splitext(output_file)[0] + '.json'
        
        df.to_csv(csv_file, index=False)
        df.to_parquet(pq_file, index=False)
        df.to_json(json_file, orient='records', indent=2)
        
        print(f"Dataset saved to:\n- {csv_file}\n- {pq_file}\n- {json_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create ML dataset from YOLOv8 segmentation data.')
    parser.add_argument('directory', type=str, help='Directory containing YOLOv8 .txt files')
    parser.add_argument('--output', type=str, default='ellipse_dataset', 
                       help='Output filename (without extension unless --csv-only)')
    parser.add_argument('--csv-only', action='store_true', 
                       help='Save only CSV format (automatically adds .csv extension if not present)')
    
    args = parser.parse_args()
    
    df = process_directory(args.directory)
    save_dataset(df, args.output, csv_only=args.csv_only)
    
    # Print dataset summary
    print("\nDataset Summary:")
    print(f"Total records: {len(df)}")
    print(f"Unique frames: {df['frame_id'].nunique()}")
    print(f"Classes found: {sorted(df['class_id'].unique())}")
    print("\nFirst 5 records:")
    print(df.head())
