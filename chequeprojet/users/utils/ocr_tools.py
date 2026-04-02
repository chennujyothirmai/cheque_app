import cv2
import pytesseract


def clean_ocr_region(img):
    """Preprocess region before OCR – improves results 10x."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # remove noise
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # strong threshold for printed text
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, 9
    )
    return thresh


def ocr_text(img):
    pre = clean_ocr_region(img)
    text = pytesseract.image_to_string(pre, config="--psm 6")
    return text.strip()
