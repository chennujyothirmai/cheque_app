import os

import cv2
import joblib
import matplotlib
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from PIL import Image
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from torchvision import datasets, transforms

from .forms import ImageUploadForm, RegistrationForm
from .models import UserAccount
from .utils.final_pipeline import process_cheque
from .utils.gemini_extract import extract_cheque_info

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def basefunction(request):
    """
    Landing Page View
    Title: Verifying Bank Cheques using Deep Learning and Image Processing
    Button: Get Started (Navigates to Login)
    """
    return render(request, "base.html")


def userlogin(request):
    """
    Single Unified Login (Role-Based)
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # 1. ADMIN CHECK (admin/admin)
        if username == "admin" and password == "admin":
            request.session['admin_logged_in'] = True
            messages.success(request, "Admin login successful!")
            return redirect("adminhome")

        # 2. USER CHECK
        try:
            user = UserAccount.objects.get(username=username)
            if user.check_password(password):
                if user.status == "activated":
                    request.session["user_id"] = user.id
                    messages.success(request, f"Welcome {user.username}!")
                    return redirect("userhome")
                elif user.status == "blocked":
                    messages.error(request, "Your account is blocked. Contact Admin!")
                else:
                    messages.warning(request, f"Your status is '{user.status}'. Access Denied.")
            else:
                messages.error(request, "Incorrect password!")
        except UserAccount.DoesNotExist:
            messages.error(request, "Account not found!")

    return render(request, "userlogin.html")


# ===========================
# Registration View
# ===========================
def register(request):
    print("Register view called.")

    if request.method == "POST":
        print("POST request received.")
        form = RegistrationForm(request.POST)
        print("Form instantiated with POST data.")

        if form.is_valid():
            print("Form is valid.")
            user = form.save(commit=False)
            print(f"User object created: {user.username}, {user.email}")

            # Hash password
            raw_password = form.cleaned_data["password"]
            user.set_password(raw_password)
            print("Password hashed successfully.")

            # Default status
            user.status = "waiting"
            user.save()
            print(f"User saved to DB with status: {user.status}")

            # Success message
            messages.success(
                request,
                "Account created successfully! Waiting for activation.",
            )
            print("Success message added to messages framework.")
            return redirect("userlogin")
        else:
            print("Form is NOT valid. Printing errors:")
            for field in form.errors:
                for error in form.errors[field]:
                    print(f"Field: {field}, Error: {error}")
                    messages.error(request, f"{field}: {error}")

    else:
        print("GET request received. Rendering blank form.")
        form = RegistrationForm()

    print("Rendering register.html template.")
    return render(request, "register.html", {"form": form})


# ===========================
# User Home View
# ===========================
def userhome(request):
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "You must login first!")
        print("No session found. Redirecting to login.")
        return redirect("userlogin")

    try:
        user = UserAccount.objects.get(id=user_id)
    except UserAccount.DoesNotExist:
        messages.error(request, "User not found!")
        return redirect("basefunction")

    return render(request, "userhome.html", {"user": user})


def logout_view(request):
    user_id = request.session.get("user_id")
    if user_id:
        print(f"Logging out user id: {user_id}")
        request.session.flush()
        messages.success(request, "Logged out successfully!")
    else:
        print("Logout called but no user session found.")
        messages.warning(request, "You are not logged in!")
    return redirect("userlogin")


def cheque_samples(request):
    dataset_dir = os.path.join(settings.MEDIA_ROOT, "cheque_data/images/train/fixed")
    images = []
    if os.path.exists(dataset_dir):
        for f in os.listdir(dataset_dir):
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                images.append(settings.MEDIA_URL + "cheque_data/images/train/fixed/" + f)
                if len(images) >= 12:  # Limit images to avoid overload
                    break
    return render(request, "ChequeSamples.html", {"images": images})


# END CHEQUE SAMPLES


def prediction(request):
    uploaded_image = None
    output = None
    details = None
    error = None

    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)

        if form.is_valid():
            img_file = form.cleaned_data.get("image")

            if not img_file:
                return render(
                    request,
                    "predictForm1.html",
                    {"form": form, "error": "Please upload an image"},
                )

            save_dir = os.path.join(settings.MEDIA_ROOT, "uploaded")
            os.makedirs(save_dir, exist_ok=True)

            original_ext = img_file.name.split(".")[-1].lower()
            img_save_name = img_file.name

            # ---------------- TIFF → JPG ----------------
            if original_ext in ["tif", "tiff"]:
                img = Image.open(img_file).convert("RGB")
                img_save_name = img_file.name.rsplit(".", 1)[0] + ".jpg"
                save_path = os.path.join(save_dir, img_save_name)
                img.save(save_path, "JPEG", quality=95)
            else:
                save_path = os.path.join(save_dir, img_save_name)
                with open(save_path, "wb+") as f:
                    for chunk in img_file.chunks():
                        f.write(chunk)

            uploaded_image = f"{settings.MEDIA_URL}uploaded/{img_save_name}"

            # ==========================================================
            # 🚀 OPTIMIZED: Combined Validation & Extraction in ONE Call
            # ==========================================================
            gemini_result = extract_cheque_info(save_path)

            if not gemini_result.get("is_cheque", False):
                reason = gemini_result.get("message", "Not a Bank Cheque")
                return render(
                    request,
                    "predictForm1.html",
                    {
                        "form": form,
                        "uploaded_image": uploaded_image,
                        "error": "❌ Document Issue",
                        "output": f"INVALID: {reason}",
                        "details": gemini_result.get("details"),
                    },
                )

            # ✅ Robust Validation (Combines Gemini AI and Local CV Processing)
            cv_status = process_cheque(save_path)
            prediction_status = gemini_result.get("prediction", "INVALID").upper()
            details = gemini_result.get("details", {})
            
            # 1. Check Mandatory Fields from AI
            mandatory_fields = [
                'account_number', 'ifsc_code', 'cheque_number', 
                'payee_name', 'amount_words', 'amount_number'
            ]
            
            missing_fields = []
            for field in mandatory_fields:
                val = str(details.get(field, "N/A")).strip().upper()
                if val == "N/A" or val == "" or val == "NONE":
                    missing_fields.append(field.replace('_', ' ').title())

            # 2. Check Signature from CV or AI
            sig_ok = True
            if "FORGED (Signature missing)" in cv_status or details.get("signature_present") == "No":
                sig_ok = False
                missing_fields.append("Signature")

            # FINAL DECISION: STOCKS & STRICT
            if prediction_status == "VALID" and not missing_fields:
                output = "VALID"
                reason = "All mandatory fields detected and verified."
            else:
                output = "INVALID"
                if missing_fields:
                    reason = f"Missing/Unreadable fields: {', '.join(missing_fields)}"
                else:
                    reason = gemini_result.get("message", "Security validation failed")

            # Add CV insight to details for UI
            details["cv_analysis"] = cv_status

            details = gemini_result.get("details")

        else:
            error = "Invalid form submission"

    else:
        form = ImageUploadForm()

    return render(
        request,
        "predictForm1.html",
        {
            "form": form,
            "uploaded_image": uploaded_image,
            "output": output,
            "details": details,
            "error": error,
        },
    )


# END PREDICTION


# ============================================================
#  CNN ARCHITECTURE (same as training)
# ============================================================
class ChequeDigitCNN(nn.Module):
    def __init__(self):
        super(ChequeDigitCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 64 * 7 * 7)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


# ============================================================
#  SIFT EXTRACTION
# ============================================================
def extract_sift_features(image_path, vector_size=128):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None

    sift = cv2.SIFT_create()
    kp, desc = sift.detectAndCompute(img, None)

    if desc is None:
        return None

    desc = desc.flatten()

    if len(desc) < vector_size:
        desc = np.pad(desc, (0, vector_size - len(desc)))
    else:
        desc = desc[:vector_size]

    return desc


# ============================================================
#  SAVE CONFUSION MATRIX
# ============================================================
def save_confusion_matrix(y_true, y_pred, name):
    cm = confusion_matrix(y_true, y_pred)

    plt.figure(figsize=(6, 5))
    plt.imshow(cm, cmap="Blues")
    plt.colorbar()
    plt.title(name)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    for i in range(len(cm)):
        for j in range(len(cm[0])):
            plt.text(j, i, cm[i, j], ha="center", va="center")

    eval_dir = os.path.join(settings.MEDIA_ROOT, "evaluation")
    os.makedirs(eval_dir, exist_ok=True)

    file_path = os.path.join(eval_dir, name.replace(" ", "_") + ".png")
    plt.savefig(file_path)
    plt.close()

    return settings.MEDIA_URL + "evaluation/" + name.replace(" ", "_") + ".png"


# ============================================================
#  SAVE BAR CHART
# ============================================================
def save_bar_chart(metrics_dict, name):
    labels = list(metrics_dict.keys())
    values = list(metrics_dict.values())

    plt.figure(figsize=(7, 4))
    plt.bar(labels, values)
    plt.ylim(0, 1)
    plt.title(name)

    eval_dir = os.path.join(settings.MEDIA_ROOT, "evaluation")
    os.makedirs(eval_dir, exist_ok=True)

    file_path = os.path.join(eval_dir, name.replace(" ", "_") + ".png")
    plt.savefig(file_path)
    plt.close()

    return settings.MEDIA_URL + "evaluation/" + name.replace(" ", "_") + ".png"


# ============================================================
#  FULL MODEL EVALUATION VIEW
# ============================================================
def model_evaluation(request):

    # ----------------------------------------------------------------------
    # 1️⃣ SIGNATURE SVM MODEL
    # ----------------------------------------------------------------------
    svm_path = os.path.join(
        settings.MEDIA_ROOT, "signature_model/svm_signature.pkl"
    )
    scaler_path = os.path.join(
        settings.MEDIA_ROOT, "signature_model/svm_scaler.pkl"
    )

    svm = joblib.load(svm_path)
    scaler = joblib.load(scaler_path)

    # Correct signature dataset path
    sig_root = os.path.join(
        settings.MEDIA_ROOT,
        "signature_dataset/Dataset_Signature_Final/dataset1",
    )

    real_dir = os.path.join(sig_root, "real")
    forge_dir = os.path.join(sig_root, "forge")

    X_sig = []
    y_sig = []

    # Fetch REAL signatures
    if os.path.exists(real_dir):
        for f in os.listdir(real_dir):
            if f.lower().endswith((".jpg", ".png", ".jpeg")):
                feat = extract_sift_features(os.path.join(real_dir, f))
                if feat is not None:
                    X_sig.append(feat)
                    y_sig.append(1)

    # Fetch FORGED signatures
    if os.path.exists(forge_dir):
        for f in os.listdir(forge_dir):
            if f.lower().endswith((".jpg", ".png", ".jpeg")):
                feat = extract_sift_features(os.path.join(forge_dir, f))
                if feat is not None:
                    X_sig.append(feat)
                    y_sig.append(0)

    X_sig = np.array(X_sig)
    y_sig = np.array(y_sig)

    # Prevent crash if dataset empty
    if not os.path.exists(real_dir) or len(X_sig) == 0:
        return render(
            request,
            "ModelEvaluation.html",
            {
                "sig_error": "Signature dataset not found on server yet!",
                "digit_acc": 0, "digit_pre": 0, "digit_rec": 0, "digit_f1": 0
            },
        )

    X_scaled = scaler.transform(X_sig)
    y_sig_pred = svm.predict(X_scaled)

    sig_acc = accuracy_score(y_sig, y_sig_pred)
    sig_pre = precision_score(y_sig, y_sig_pred)
    sig_rec = recall_score(y_sig, y_sig_pred)
    sig_f1 = f1_score(y_sig, y_sig_pred)

    sig_cm_img = save_confusion_matrix(
        y_sig, y_sig_pred, "Signature Confusion Matrix"
    )
    sig_bar_img = save_bar_chart(
        {
            "Accuracy": sig_acc,
            "Precision": sig_pre,
            "Recall": sig_rec,
            "F1": sig_f1,
        },
        "Signature Metrics",
    )

    # ----------------------------------------------------------------------
    # 2️⃣ DIGIT CNN MODEL
    # ----------------------------------------------------------------------
    cnn_path = os.path.join(settings.MEDIA_ROOT, "digit_cnn.pth")

    digit_model = ChequeDigitCNN()
    digit_model.load_state_dict(torch.load(cnn_path, map_location="cpu"))
    digit_model.eval()

    mnist_path = os.path.join(settings.MEDIA_ROOT, "minist")

    transform = transforms.Compose(
        [
            transforms.Grayscale(),
            transforms.Resize((28, 28)),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,)),
        ]
    )

    test_dataset = datasets.MNIST(
        mnist_path, train=False, download=True, transform=transform
    )
    test_loader = torch.utils.data.DataLoader(
        test_dataset, batch_size=64, shuffle=False
    )

    y_true = []
    y_pred = []

    with torch.no_grad():
        for images, labels in test_loader:
            outputs = digit_model(images)
            _, predict = torch.max(outputs, 1)
            y_true.extend(labels.numpy())
            y_pred.extend(predict.numpy())

    digit_acc = accuracy_score(y_true, y_pred)
    digit_pre = precision_score(y_true, y_pred, average="macro")
    digit_rec = recall_score(y_true, y_pred, average="macro")
    digit_f1 = f1_score(y_true, y_pred, average="macro")

    digit_cm_img = save_confusion_matrix(
        y_true, y_pred, "Digit CNN Confusion Matrix"
    )
    digit_bar_img = save_bar_chart(
        {
            "Accuracy": digit_acc,
            "Precision": digit_pre,
            "Recall": digit_rec,
            "F1": digit_f1,
        },
        "Digit CNN Metrics",
    )

    # ----------------------------------------------------------------------
    # 3️⃣ RETURN DATA TO HTML
    # ----------------------------------------------------------------------
    return render(
        request,
        "ModelEvaluation.html",
        {
            # Signature
            "sig_acc": sig_acc,
            "sig_pre": sig_pre,
            "sig_rec": sig_rec,
            "sig_f1": sig_f1,
            "sig_cm": sig_cm_img,
            "sig_bar": sig_bar_img,
            # Digit CNN
            "digit_acc": digit_acc,
            "digit_pre": digit_pre,
            "digit_rec": digit_rec,
            "digit_f1": digit_f1,
            "digit_cm": digit_cm_img,
            "digit_bar": digit_bar_img,
        },
    )
