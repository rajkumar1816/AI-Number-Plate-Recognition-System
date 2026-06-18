import traceback
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import load_settings
from detector.detector import YOLODetector
from preprocessing.image_processor import preprocess_image
from ocr.ocr_engine import read_plate_text
from ocr.text_cleaner import normalize_plate_text, validate_plate_text


def simulate(image_path: Path):
    settings = load_settings()
    detector = YOLODetector(settings.MODEL_NAME)
    print('Model:', detector.model_path)
    try:
        dets = detector.detect_plate(image_path, conf_threshold=settings.CONFIDENCE_THRESHOLD)
        print('Detections:', dets)
        if not dets:
            print('No detections')
            return
        best = dets[0]
        bbox = best['bbox']
        crop_name = image_path.stem + '_plate_crop.jpg'
        crop_path = detector.crop_plate(image_path, bbox, Path('storage') / 'crops' / crop_name)
        print('Cropped:', crop_path)
        preprocess_image(crop_path)
        ocr_results = read_plate_text(str(crop_path))
        print('OCR results:', ocr_results)
        best_result = max(ocr_results, key=lambda item: item['confidence'])
        print('Best OCR:', best_result)
        cleaned_text = normalize_plate_text(best_result['text'])
        print('Cleaned:', cleaned_text)
        valid, normalized = validate_plate_text(cleaned_text)
        print('Valid:', valid, 'Normalized:', normalized)
    except Exception:
        traceback.print_exc()


if __name__ == '__main__':
    val_dir = Path('data/plates_dataset/images/val')
    for img in val_dir.iterdir():
        if img.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            print('\n---', img)
            simulate(img)
            # stop after first simulation to keep output short
            break
