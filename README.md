Takes an annotations file in COCO 1.0 format and the images it corresponds to and overlays the annotations on the images.

# Usage

```bash
python visualize_annotations.py --annotations annotations/instances_default.json --images input_images/
```

# Arguments

- `--annotations`: Path to the annotations file in COCO 1.0 format.
- `--images`: Path to the folder containing the images corresponding to the annotations.

# Output

The script will create a folder named `annotated_images` in the current directory, which will contain the annotated images.
