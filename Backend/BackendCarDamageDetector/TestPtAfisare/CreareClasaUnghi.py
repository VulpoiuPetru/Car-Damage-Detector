from ultralytics import YOLO
import os
import cv2
import numpy as np

class CarDirectionDetector:
    def __init__(self,model_path):
        # Verifică dacă modelul există
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelul {model_path} nu a fost găsit!")

        # Încarcă modelul o singură dată
        self.model = YOLO(model_path)
    def detect_direction(self,image_path):
        # Încarcă imaginea
        original_image = cv2.imread(image_path)
        if original_image is None:
            raise ValueError(f"Eroare la încărcarea imaginii {image_path}")

        # Rulează YOLO pe imagine
        results = self.model(image_path)[0]

        # Extrage detecțiile
        boxes = results.boxes.xyxy.cpu().numpy()
        scores = results.boxes.conf.cpu().numpy()
        labels = results.boxes.cls.cpu().numpy()

        print(f"\nImagine: {os.path.basename(image_path)}")
        print(f"Clase detectate: {labels}")

        # Variabile pentru Front, Back și Side
        front_box, back_box, side_box = None, None, None

        for label, score, box in zip(labels, scores, boxes):
            if label == 0:  # Front
                front_box = box
                print(f"Front detectat la: {front_box}")
            elif label == 1:  # Back
                back_box = box
                print(f"Back detectat la: {back_box}")
            elif label == 2:  # Side
                side_box = box
                print(f"Side detectat la: {side_box}")

            # Verifică combinațiile de clase detectate
        detected_classes = set(labels)
        direction = None  # Inițializăm direcția cu None

        if detected_classes == {0, 1, 2}:  # Toate trei
            if front_box is not None and back_box is not None and side_box is not None:
                if front_box[0] < back_box[0]:  # Comparăm coordonatele X
                    direction = "Stanga"
                elif front_box[0] > back_box[0]:
                    direction = "Dreapta"

                print(f"Directie detectată: {direction}")

        elif detected_classes == {0, 2}:  # Front și Side
            if front_box is not None and side_box is not None:
                if front_box[0] < side_box[0]:  # Comparăm coordonatele X
                    direction = "Stanga"
                else:
                    direction = "Dreapta"

                print(f"Directie detectată: {direction}")

        elif detected_classes == {1, 2}:  # Back și Side
            if back_box is not None and side_box is not None:
                if back_box[0] > side_box[0]:
                    direction = "Stanga"
                else:
                    direction = "Dreapta"

                print(f"Directie detectată: {direction}")

        else:
            print(f"Imaginea {os.path.basename(image_path)} NU conține doar Front și Side sau Back și Side!")

        return direction




