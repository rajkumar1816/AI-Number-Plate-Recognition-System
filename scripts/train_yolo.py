import argparse
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='yolov8n.pt')
    parser.add_argument('--data', required=True)
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--name', default='plates_quick')
    args = parser.parse_args()

    model = YOLO(args.model)
    model.train(data=args.data, epochs=args.epochs, imgsz=args.imgsz, name=args.name)


if __name__ == '__main__':
    main()
