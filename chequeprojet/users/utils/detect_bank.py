import cv2
import pytesseract


def detect_bank_type(img_path):

    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    # crop top-left 25% area
    roi = img[0 : int(0.25 * h), 0 : int(0.40 * w)]

    text = pytesseract.image_to_string(roi, config="--psm 6").lower()

    if "syndicate" in text:
        return "syndicate"
    if "icici" in text:
        return "icici"
    if "axis" in text:
        return "axis"
    if "canara" in text:
        return "canara"

    return "unknown"
