from digit_cnn import train_digit_cnn

print("Training Handwritten Digit CNN (as per PDF)...")
model = train_digit_cnn(
    num_epochs=2, batch_size=64, lr=0.001  # keep small for testing
)
print("Training Completed.")
