"""Debug script to test detection with various confidence thresholds."""
import cv2
from pathlib import Path
from ultralytics import YOLO

# Load model
model = YOLO('runs/detect/plates_10epochs/weights/best.pt')

# Test on a sample image
test_image = 'data/plates_dataset/images/val'
image_files = list(Path(test_image).glob('*.jpg'))

if not image_files:
    print("No images found in validation folder")
    exit(1)

# Test with first image at different confidence levels
img_path = str(image_files[0])
print(f"Testing with: {img_path}\n")

for conf in [0.1, 0.05, 0.01, 0.001]:
    print(f"Confidence threshold: {conf}")
    results = model.predict(source=img_path, conf=conf, verbose=False)
    
    for result in results:
        boxes = result.boxes
        print(f"  Detections: {len(boxes)}")
        for box in boxes:
            print(f"    - Confidence: {box.conf.item():.4f}, Class: {int(box.cls.item())}")
    
    if not results[0].boxes:
        print(f"  No detections at conf={conf}")
    print()

# Also check raw model output
print("\n--- Raw Model Output ---")
results = model.predict(source=img_path, conf=0.001, verbose=True)
