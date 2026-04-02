import os

import cv2


def extract_digits_from_amount(img, save_dir, prefix):
    """
    Extract digits from courtesy/legal amount box.
    Saves each digit as an image to build your custom dataset.
    """

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, th = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # find digit contours
    contours, _ = cv2.findContours(
        th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    os.makedirs(save_dir, exist_ok=True)
    idx = 0

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h < 25 or w < 10:  # small noise
            continue

        digit = th[y : y + h, x : x + w]
        digit = cv2.resize(digit, (28, 28))

        cv2.imwrite(os.path.join(save_dir, f"{prefix}_{idx}.png"), digit)
        idx += 1

    return idx
