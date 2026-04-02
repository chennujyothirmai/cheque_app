import os

import cv2
import joblib
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    recall_score,
)
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def load_signature_images(root_path):
    """Loads all genuine and forged signatures from every dataset directory."""
    print("[INFO] Loading Signature Dataset (ALL DATASETS)...")

    genuine_paths = []
    forged_paths = []

    # Folders for genuine signatures
    genuine_dirs = [
        "dataset1/real",
        "dataset2/real",
        "dataset3/real",
        "dataset4/real",
        "sample_Signature/genuine",
    ]

    # Folders for forged signatures
    forged_dirs = [
        "dataset1/forge",
        "dataset3/forge",
        "dataset4/forge",
        "sample_Signature/forged",
    ]

    for g_dir in genuine_dirs:
        full = os.path.join(root_path, g_dir)
        if os.path.exists(full):
            for img_name in os.listdir(full):
                if img_name.lower().endswith((".jpg", ".png", ".jpeg")):
                    genuine_paths.append(os.path.join(full, img_name))

    for f_dir in forged_dirs:
        full = os.path.join(root_path, f_dir)
        if os.path.exists(full):
            for img_name in os.listdir(full):
                if img_name.lower().endswith((".jpg", ".png", ".jpeg")):
                    forged_paths.append(os.path.join(full, img_name))

    print(f"[INFO] Genuine Images: {len(genuine_paths)}")
    print(f"[INFO] Forged Images: {len(forged_paths)}")

    return genuine_paths, forged_paths


def extract_sift_features(image_path, vector_size=128):
    """SIFT Feature Extraction according to PDF (Page 5-6)."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None

    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(img, None)

    if descriptors is None:
        return None

    descriptor = descriptors.flatten()

    # Pad or crop to 128 values as per PDF
    if descriptor.size < vector_size:
        descriptor = np.pad(
            descriptor, (0, vector_size - descriptor.size), mode="constant"
        )
    else:
        descriptor = descriptor[:vector_size]

    return descriptor


def train_signature_svm(signature_root, save_dir):
    print("\n========== TRAINING SIGNATURE SVM (PDF METHOD) ==========\n")

    genuine_paths, forged_paths = load_signature_images(signature_root)

    X = []
    y = []

    print("[INFO] Extracting SIFT features...")

    for path in genuine_paths:
        feat = extract_sift_features(path)
        if feat is not None:
            X.append(feat)
            y.append(1)  # 1 = Genuine

    for path in forged_paths:
        feat = extract_sift_features(path)
        if feat is not None:
            X.append(feat)
            y.append(0)  # 0 = Forged

    X = np.array(X)
    y = np.array(y)

    print(f"[INFO] Total Features Extracted: {len(X)}")

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    svm = SVC(kernel="rbf", probability=True)
    svm.fit(X_scaled, y)

    # Predictions for internal evaluation
    y_pred = svm.predict(X_scaled)

    acc = accuracy_score(y, y_pred)
    rec = recall_score(y, y_pred)
    f1 = f1_score(y, y_pred)

    print("\n===== Signature SVM Metrics (Internal Evaluation) =====")
    print("Accuracy:", acc)
    print("Recall:", rec)
    print("F1 Score:", f1)
    print("\nClassification Report:\n", classification_report(y, y_pred))

    # Save model & scaler
    os.makedirs(save_dir, exist_ok=True)
    joblib.dump(svm, os.path.join(save_dir, "svm_signature.pkl"))
    joblib.dump(scaler, os.path.join(save_dir, "svm_scaler.pkl"))

    print(f"\n[INFO] Signature Model Saved At: {save_dir}")

    return svm, scaler
