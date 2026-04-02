import os
from glob import glob

import cv2

# --------------------------------------------
# STEP 1 — IMAGE ACQUISITION (PDF Page 4)
# --------------------------------------------


def load_cheque_images(base_path):
    """
    Loads cheque images from train folder.
    Exact technique described in PDF:
    - System accepts scanned cheque images.
    - Images stored in structured directories.
    """
    image_dir = os.path.join(base_path, "images", "train")
    image_paths = glob(os.path.join(image_dir, "*.jpg")) + glob(
        os.path.join(image_dir, "*.png")
    )

    print(f"[INFO] Loaded {len(image_paths)} cheque images.")
    return image_paths


# --------------------------------------------
# STEP 2 — PREPROCESSING (PDF Page 4)
# Rotation → Noise Removal → Grayscale → Gaussian Filter → Binary
# --------------------------------------------


def detect_date_box_and_correct_rotation(image):
    """
    PDF says: 'Orientation and rotation are corrected using the date field.'
    We detect regions similar to a date box & use their bounding box angle.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    angle = 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Date boxes are typically long rectangular boxes
        if w > 100 and 20 < h < 60:
            rect = cv2.minAreaRect(cnt)
            angle = rect[-1]

            # cv2 gives angle in a weird negative format → normalize
            if angle < -45:
                angle = 90 + angle

            break

    # Rotate the full image using angle found
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR)

    return corrected


def preprocess_image(img_path):
    """
    Returns a DICTIONARY ONLY. Never returns a tuple.
    """

    # Read image
    image = cv2.imread(img_path)
    if image is None:
        print("[ERROR] Unable to load:", img_path)
        return None

    # Rotation correction
    rotated = detect_date_box_and_correct_rotation(image)

    # Convert to gray
    gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)

    # Gaussian smoothing
    gaussian = cv2.GaussianBlur(gray, (5, 5), 0)

    # Binary conversion
    binary = cv2.adaptiveThreshold(
        gaussian,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2,
    )

    # Return DICTIONARY ONLY — NO TUPLE
    return {
        "original": image,
        "rotated": rotated,
        "gray": gray,
        "gaussian": gaussian,
        "binary": binary,
    }
