import json
import cv2
import numpy as np
import os
from pathlib import Path
import colorsys
import argparse

def create_distinct_colors(n):
    """Create n visually distinct colors."""
    colors = []
    for i in range(n):
        hue = i / n
        saturation = 0.9
        value = 0.9
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        # Convert to BGR for OpenCV and scale to 0-255
        bgr = (int(rgb[2] * 255), int(rgb[1] * 255), int(rgb[0] * 255))
        colors.append(bgr)
    return colors

def draw_polygon(image, points, color, category_name):
    """Draw a polygon and add category label."""
    # Convert points from flat list to array of points
    points = np.array(points).reshape((-1, 2)).astype(np.int32)
    
    # Draw the polygon
    cv2.polylines(image, [points], True, color, 2)
    
    # Fill polygon with semi-transparent color
    overlay = image.copy()
    cv2.fillPoly(overlay, [points], color)
    cv2.addWeighted(overlay, 0.3, image, 0.7, 0, image)
    
    # Add category label near the polygon
    text_pos = (points.min(axis=0)[0], points.min(axis=0)[1] - 10)
    cv2.putText(image, category_name, text_pos, 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def main(annotations_path, image_folder):
    # Create output directory if it doesn't exist
    output_dir = Path("annotated_images")
    output_dir.mkdir(exist_ok=True)
    
    # Load COCO annotations
    with open(annotations_path, 'r') as f:
        coco_data = json.load(f)
    
    # Create category id to name mapping
    category_map = {cat['id']: cat['name'] for cat in coco_data['categories']}
    
    # Create distinct colors for each category
    colors = create_distinct_colors(len(category_map))
    color_map = {cat_id: colors[i] for i, cat_id in enumerate(category_map.keys())}
    
    # Process each image
    for img_info in coco_data['images']:
        img_id = img_info['id']
        img_filename = img_info['file_name']
        
        # Load image
        img_path = os.path.join(image_folder, img_filename)
        if not os.path.exists(img_path):
            print(f"Warning: Image {img_filename} not found")
            continue
            
        image = cv2.imread(img_path)
        if image is None:
            print(f"Warning: Could not load image {img_filename}")
            continue
        
        # Find annotations for this image
        img_annotations = [ann for ann in coco_data['annotations'] 
                         if ann['image_id'] == img_id]
        
        # Draw each annotation
        for ann in img_annotations:
            category_id = ann['category_id']
            category_name = category_map[category_id]
            color = color_map[category_id]
            
            # Draw each polygon in the segmentation
            for polygon in ann['segmentation']:
                draw_polygon(image, polygon, color, category_name)
        
        # Save annotated image
        output_path = output_dir / f"annotated_{img_filename}"
        cv2.imwrite(str(output_path), image)
        print(f"Processed {img_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize COCO annotations on images')
    parser.add_argument('--annotations', type=str, default="annotations/instances_default.json",
                      help='Path to the COCO annotations JSON file')
    parser.add_argument('--images', type=str, default="input_images/",
                      help='Path to the folder containing images')
    
    args = parser.parse_args()
    
    main(args.annotations, args.images)
