import os
import torch
from ultralytics import YOLO

# def train_model():
#     # Încarcă modelul antrenat anterior
#     model = YOLO("runs/detect/train44/weights/last.pt")  # Sau best.pt dacă vrei cea mai bună versiune
#
#     # Rulează antrenarea
#     results = model.train(data="config.yaml", epochs=5, project="runs/detect", name="train44")

#rulare pe procesor
def train_model():
    # Setează dispozitivul pe CPU
    device = torch.device("cpu")

    # Încarcă modelul antrenat anterior, forțând rularea pe CPU
    model = YOLO("runs/detect/train632/weights/last.pt").to(device)  # Sau best.pt dacă vrei cea mai bună versiune

    # Rulează antrenarea, setând device la CPU
    results = model.train(data="config.yaml", epochs=15, project="runs/detect", name="train632", device="cpu")


if __name__ == "__main__":
    train_model()