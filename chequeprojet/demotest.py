import imghdr
import os

folder = r"E:\Verifying bank checks using deep learning and image processing\code\chequeproject\chequeprojet\media\cheque_data\images\train"

for file in os.listdir(folder):
    if file.endswith(".jpg"):
        f = os.path.join(folder, file)
        print(file, "->", imghdr.what(f))
