import cv2
import numpy as np

# ---------------------------------------------------------
# STEP 1 — LOAD IMAGE + PREPROCESS
# ---------------------------------------------------------


def preprocess(img_path):
    img = cv2.imread(img_path)

    if img is None:
        return None, "Image load failed"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Remove noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Edge detection
    edges = cv2.Canny(blur, 80, 180)

    return img, edges


# ---------------------------------------------------------
# STEP 2 — FIND CHEQUE OUTLINE (Largest rectangle)
# ---------------------------------------------------------


def detect_cheque_outline(edges):
    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if len(contours) == 0:
        return None

    # Largest contour = cheque boundary
    cnt = max(contours, key=cv2.contourArea)

    area = cv2.contourArea(cnt)

    # Cheque must have a reasonable rectangular region
    if area < 30000: # Lowered from 50000
        return None

    return cnt


# ---------------------------------------------------------
# STEP 3 — DETECT SIGNATURE AREA
# Bottom-right quadrant of the cheque
# ---------------------------------------------------------


def detect_signature(img):
    h, w = img.shape[:2]

    # signature block is usually bottom-right of cheque
    sig_region = img[
        int(h * 0.55) : int(h * 0.95), int(w * 0.50) : int(w * 0.98)
    ]

    gray = cv2.cvtColor(sig_region, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    ink_pixels = np.sum(thresh == 255)

    # signature must have enough ink pixels
    if ink_pixels > 800: # Lowered from 1500 for better detection of smaller signatures
        return True  # signature exists
    return False  # signature missing


# ---------------------------------------------------------
# STEP 4 — CHECK BLUR (for tampering)
# ---------------------------------------------------------


def is_blurry(gray):
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Very low variance = blurred image
    return laplacian_var < 30 # Lowered from 60 to allow lower resolution images


# ---------------------------------------------------------
# STEP 5 — FINAL DECISION
# ---------------------------------------------------------


def process_cheque(img_path):
    img, edges = preprocess(img_path)

    if img is None:
        return "ERROR: Could not load image"

    # 1. Detect cheque boundary
    cheque_outline = detect_cheque_outline(edges)
    # We won't fail here because many users upload cropped images
    # If cheque_outline is None:
    #     return "FORGED (Cheque boundary missing)"

    # 2. Check signature
    signature_ok = detect_signature(img)
    if not signature_ok:
        return "FORGED (Signature missing)"

    # 3. Blur / tampering check
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if is_blurry(gray):
        return "FORGED (Cheque is blurred / tampered)"

    # If passed all checks:
    return "VALID"
