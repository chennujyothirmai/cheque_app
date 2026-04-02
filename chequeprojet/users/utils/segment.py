import os

import cv2


def segment_cheque_regions(img_path, save_folder):

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    img = cv2.imread(img_path)
    if img is None:
        print("Error loading", img_path)
        return None

    h, w = img.shape[:2]

    # Correct ROI positions for Syndicate Bank cheque
    roi_boxes = {
        "ifsc_code": (
            int(0.72 * w),
            int(0.03 * h),
            int(0.98 * w),
            int(0.13 * h),
        ),
        "account_number": (
            int(0.10 * w),
            int(0.40 * h),
            int(0.90 * w),
            int(0.55 * h),
        ),
        "cheque_number": (
            int(0.80 * w),
            int(0.88 * h),
            int(0.98 * w),
            int(0.96 * h),
        ),
        "legal_amount": (
            int(0.10 * w),
            int(0.22 * h),
            int(0.90 * w),
            int(0.35 * h),
        ),
        "courtesy_amount": (
            int(0.70 * w),
            int(0.32 * h),
            int(0.98 * w),
            int(0.45 * h),
        ),
        "signature": (
            int(0.70 * w),
            int(0.60 * h),
            int(0.98 * w),
            int(0.80 * h),
        ),
    }

    extracted = {}

    for name, (x1, y1, x2, y2) in roi_boxes.items():
        crop = img[y1:y2, x1:x2]
        crop_path = os.path.join(save_folder, f"{name}.png")
        cv2.imwrite(crop_path, crop)
        extracted[name] = crop_path

    print("\n✔ Correct segmentation completed\n")
    return extracted


def segment_cheque(img_path):
    save_folder = os.path.join(os.path.dirname(img_path), "segmented_regions")
    return segment_cheque_regions(img_path, save_folder)
