import os

import cv2

from .segment_router import segment_cheque


def extract_digits(img, save_dir, prefix):
    """
    Extract individual digits using contours.
    Saves into dataset folders: dataset/digits/0,1,2,...,9
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    th = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 7
    )

    contours, _ = cv2.findContours(
        th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    idx = 0

    os.makedirs(save_dir, exist_ok=True)

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h < 25 or w < 10:
            continue

        digit = th[y : y + h, x : x + w]
        digit = cv2.resize(digit, (28, 28))

        cv2.imwrite(os.path.join(save_dir, f"{prefix}_{idx}.png"), digit)
        idx += 1

    return idx


def build_digit_dataset(dataset_root, save_root):
    """
    For ALL cheque images in dataset, segment → extract amount digits → save.
    """
    os.makedirs(save_root, exist_ok=True)

    images = []
    for folder in ["train", "val", "validation", "images/train", "images/val"]:
        full = os.path.join(dataset_root, folder)
        if os.path.exists(full):
            for img_name in os.listdir(full):
                if img_name.lower().endswith((".png", ".jpg", ".jpeg")):
                    images.append(os.path.join(full, img_name))

    print(f"[INFO] Total cheque images found: {len(images)}")

    total = 0
    for img_path in images:
        print(f"[INFO] Processing: {img_path}")
        regions = segment_cheque(img_path)

        legal = cv2.imread(regions["legal_amount"])
        courtesy = cv2.imread(regions["courtesy_amount"])

        # For each cheque, put digits in one folder
        cheque_folder = os.path.join(
            save_root, os.path.splitext(os.path.basename(img_path))[0]
        )
        os.makedirs(cheque_folder, exist_ok=True)

        total += extract_digits(legal, cheque_folder, "legal")
        total += extract_digits(courtesy, cheque_folder, "courtesy")

    print("\n======================")
    print("[DONE] Digit dataset built successfully.")
    print(f"[TOTAL DIGITS SAVED] = {total}")
    print("======================\n")
