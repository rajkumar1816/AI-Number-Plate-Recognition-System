# AI Number Plate Recognition System

An enterprise-style Automatic Number Plate Recognition (ANPR) project built with Python, Streamlit, OpenCV, YOLOv8, EasyOCR, and SQLite.

## Project Structure

- `app.py` - Main Streamlit application entry point
- `config/` - Application settings and constants
- `database/` - SQLite database helpers and schema definitions
- `detector/` - YOLO-based plate detection engine
- `ocr/` - OCR engine and text cleanup utilities
- `preprocessing/` - Image preparation utilities
- `ui/` - Streamlit page modules for dashboard, camera, history, analytics, and settings
- `utils/` - Logging, helpers, and validators
- `storage/` - Saved images, videos, and cropped plate assets
- `logs/` - Application logs

## Install

Create a virtual environment and install dependencies:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run

Use the Python executable from the active environment to run Streamlit:

```bash
python -m streamlit run app.py
```

If `streamlit` is not on your PATH, this command ensures the correct interpreter is used.

## Model and Sample Data

The repository includes `yolov8n.pt` in the project root for YOLOv8 detection. If you need to replace or update the model, set `MODEL_NAME` in `.env` to the model filename or full path.

A sample image file `sample_plate.jpg` has been added for testing the upload flow, but a real license plate photograph is required for accurate detection and OCR.

### Trained model (latest)

I trained a YOLOv8 model on the repository dataset. The latest trained weights are saved at `runs/detect/plates_10epochs/weights/best.pt`.

- To use the new weights, ensure `.env` contains:

```
MODEL_NAME=runs/detect/plates_10epochs/weights/best.pt
```

- Restart the app to load the updated model:

```bash
streamlit run app.py
```

Prediction examples from the validation set were saved to `runs/detect/predict` during inference.

## Troubleshooting

- If the app starts but images do not detect plates, verify `yolov8n.pt` exists and the uploaded image contains a clear license plate.
- If the app fails to start, run the commands above from the project root and ensure you use the same Python interpreter that installed the dependencies.
- The app writes logs to `logs/app.log` for startup and runtime diagnostics.

## Notes

This project is a working Streamlit ANPR system with detection, OCR, persistence, analytics, and export support. The UI is designed to be extended with additional production features.
