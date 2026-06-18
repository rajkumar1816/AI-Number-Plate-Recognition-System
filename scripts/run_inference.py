import argparse
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True)
    parser.add_argument('--source', default='data/plates_dataset/images/val')
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--conf', type=float, default=0.3)
    args = parser.parse_args()

    model = YOLO(args.model)
    results = model.predict(source=args.source, imgsz=args.imgsz, conf=args.conf, save=True)
    print('Inference completed. Results saved in runs/predict/*')


if __name__ == '__main__':
    main()
