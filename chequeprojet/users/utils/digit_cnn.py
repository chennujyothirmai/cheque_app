import os

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from sklearn.metrics import accuracy_score, classification_report
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# -----------------------------
# STEP 4: CNN for Handwritten Digit Recognition
# (As per PDF page 5)
# -----------------------------


class ChequeDigitCNN(nn.Module):
    def __init__(self):
        super(ChequeDigitCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)  # digits 0-9

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 64 * 7 * 7)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


def train_digit_cnn(num_epochs=5, batch_size=64, lr=0.001):

    transform = transforms.Compose(
        [
            transforms.Grayscale(),
            transforms.Resize((28, 28)),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,)),
        ]
    )

    # Load MNIST dataset
    data_path = (
        "E:/Verifying bank checks using deep learning"
        " and image processing/code"
        "/check_classification/media/minist"
    )

    train_dataset = datasets.MNIST(
        data_path, train=True, download=True, transform=transform
    )

    test_dataset = datasets.MNIST(
        data_path, train=False, download=True, transform=transform
    )

    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False
    )

    model = ChequeDigitCNN()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    # Training Loop
    for epoch in range(num_epochs):
        running_loss = 0
        for images, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        avg_loss = running_loss / len(train_loader)
        print(
            f"Epoch {epoch+1}/{num_epochs}"
            f" - Loss: {avg_loss:.4f}"
        )

    # Evaluation
    y_true, y_pred = [], []
    model.eval()
    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            y_true.extend(labels.numpy())
            y_pred.extend(predicted.numpy())

    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred)

    print("\nCNN Digit Recognition Accuracy:", acc)
    print("\nClassification Report:\n", report)

    # Save model
    save_path = os.path.join(
        "E:/Verifying bank checks using deep learning"
        " and image processing/code"
        "/check_classification/media",
        "digit_cnn.pth",
    )
    torch.save(model.state_dict(), save_path)
    print("Model Saved At:", save_path)

    return model
