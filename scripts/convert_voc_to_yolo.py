import argparse
from pathlib import Path
import xml.etree.ElementTree as ET
import shutil
import random


def voc_to_yolo(bbox, img_w, img_h):
    xmin, ymin, xmax, ymax = bbox
    x_center = (xmin + xmax) / 2.0 / img_w
    y_center = (ymin + ymax) / 2.0 / img_h
    w = (xmax - xmin) / img_w
    h = (ymax - ymin) / img_h
    return x_center, y_center, w, h


def parse_xml(xml_path: Path):
    tree = ET.parse(str(xml_path))
    root = tree.getroot()
    size = root.find('size')
    if size is None:
        return None, []
    img_w = int(size.find('width').text)
    img_h = int(size.find('height').text)

    objects = []
    for obj in root.findall('object'):
        bnd = obj.find('bndbox')
        if bnd is None:
            continue
        xmin = int(float(bnd.find('xmin').text))
        ymin = int(float(bnd.find('ymin').text))
        xmax = int(float(bnd.find('xmax').text))
        ymax = int(float(bnd.find('ymax').text))
        objects.append((xmin, ymin, xmax, ymax))

    return (img_w, img_h), objects


def main(src_dir, dst_dir, val_split=0.2, seed=42):
    src = Path(src_dir)
    dst = Path(dst_dir)
    images_dst = dst / 'images'
    labels_dst = dst / 'labels'

    for p in (images_dst / 'train', images_dst / 'val', labels_dst / 'train', labels_dst / 'val'):
        p.mkdir(parents=True, exist_ok=True)

    xml_files = list(src.rglob('*.xml'))
    random.seed(seed)
    random.shuffle(xml_files)

    split_idx = int(len(xml_files) * (1 - val_split))
    train_files = xml_files[:split_idx]
    val_files = xml_files[split_idx:]

    def process_list(file_list, split_name):
        for xml_path in file_list:
            img_base = xml_path.with_suffix('')
            # try common image extensions
            candidates = [xml_path.with_suffix(ext) for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']]
            img_path = None
            for c in candidates:
                if c.exists():
                    img_path = c
                    break
            if img_path is None:
                # sometimes xml filename contains full image name inside <filename>
                tree = ET.parse(str(xml_path))
                root = tree.getroot()
                filename_node = root.find('filename')
                if filename_node is not None:
                    fname = filename_node.text
                    candidate = xml_path.parent / fname
                    if candidate.exists():
                        img_path = candidate
            if img_path is None:
                continue

            size, objects = parse_xml(xml_path)
            if size is None or not objects:
                continue
            img_w, img_h = size

            # copy image
            dst_img = images_dst / split_name / img_path.name
            shutil.copy2(img_path, dst_img)

            # write label file
            label_file = labels_dst / split_name / (img_path.stem + '.txt')
            with open(label_file, 'w', encoding='utf8') as f:
                for bbox in objects:
                    x_c, y_c, w, h = voc_to_yolo(bbox, img_w, img_h)
                    # single class '0' for plate
                    f.write(f"0 {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}\n")

    process_list(train_files, 'train')
    process_list(val_files, 'val')

    # write dataset yaml
    yaml_path = dst.parent / 'plates_data.yaml'
    with open(yaml_path, 'w', encoding='utf8') as y:
        y.write(f"train: {images_dst / 'train'}\n")
        y.write(f"val: {images_dst / 'val'}\n")
        y.write("nc: 1\n")
        y.write("names: ['plate']\n")

    print('Finished preparing dataset.')
    print('Dataset yaml:', yaml_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', required=True, help='Source root directory with XML and images')
    parser.add_argument('--dst', required=True, help='Destination dataset directory (will contain images/ and labels/)')
    parser.add_argument('--val-split', type=float, default=0.2)
    args = parser.parse_args()
    main(args.src, args.dst, args.val_split)
