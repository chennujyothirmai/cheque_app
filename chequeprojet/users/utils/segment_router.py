import cv2

from .detect_bank import detect_bank_type
from .segment_axis import segment_axis
from .segment_canara import segment_canara
from .segment_icici import segment_icici
from .segment_syndicate import segment_syndicate


def segment_cheque(image_path):

    img = cv2.imread(image_path)
    bank = detect_bank_type(image_path)

    print("Detected Bank:", bank)

    if bank == "syndicate":
        return segment_syndicate(img)
    if bank == "icici":
        return segment_icici(img)
    if bank == "axis":
        return segment_axis(img)
    if bank == "canara":
        return segment_canara(img)

    raise Exception("Unknown bank type — cannot segment.")
