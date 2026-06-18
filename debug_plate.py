from pathlib import Path
from detector.detector import YOLODetector
from ocr.ocr_engine import read_plate_text
from ocr.text_cleaner import normalize_plate_text, validate_plate_text

imgs = [Path('sample_plate.jpg'), Path('real_sample_plate.jpg')]
for img in imgs:
    print('===', img)
    print('exists:', img.exists())
    if not img.exists():
        continue
    detector = YOLODetector('runs/detect/plates_10epochs/weights/best.pt')
    print('model loaded:', detector.model is not None)
    print('model names:', getattr(detector.model, 'names', None))
    detections = detector.detect_plate(img, conf_threshold=0.1)
    print('YOLO detections:', detections)
    fallback = detector.fallback_detect_plate(img)
    print('Fallback detections:', fallback)
    if fallback:
        crop = detector.crop_plate(img, fallback[0]['bbox'], Path('storage/crops/test_fallback.jpg'))
        print('crop path:', crop, 'exists:', crop.exists() if crop else False)
        if crop and crop.exists():
            ocr = read_plate_text(crop)
            print('fallback OCR results:', ocr)
            if ocr:
                best = max(ocr, key=lambda item: item['confidence'])
                cleaned = normalize_plate_text(best['text'])
                valid, normalized = validate_plate_text(cleaned)
                print('best OCR', best)
                print('cleaned', cleaned, 'valid', valid, 'normalized', normalized)
