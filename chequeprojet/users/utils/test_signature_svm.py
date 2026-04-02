from signature_svm import train_signature_svm

SIGNATURE_ROOT = (
    r"E:\Verifying bank checks using deep learning"
    r" and image processing\code\check_classification"
    r"\media\signature_dataset"
)
SAVE_DIR = (
    r"E:\Verifying bank checks using deep learning"
    r" and image processing\code\check_classification"
    r"\media\signature_model"
)

train_signature_svm(SIGNATURE_ROOT, SAVE_DIR)
