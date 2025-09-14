from ultralytics import YOLO
import os
import cv2
import numpy as np

class CarDirectionDetector:
    def __init__(self,model_path):
        #verify if the model exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"The model {model_path} hasn't it find!")

        #Load the model only once for running to detect
        self.model = YOLO(model_path)

    def detect_labels(self, image_path):
        # load image
        original_image = cv2.imread(image_path)
        # veify if the image work
        if original_image is None:
            raise ValueError(f"Error to load the image {image_path}")

        # load YOLO on the image
        # Modelul YOLO este apelat cu imaginea ca intrare. Acesta efectuează detectarea obiectelor în imagine și returnează o listă de rezultate pentru fiecare cadru din imagine
        results = self.model(image_path)[0]

        labels = results.boxes.cls.cpu().numpy()  # Conține indicele clasei fiecărui obiect detectat: 0:Front,1:Back, 2:Side
        boxes = results.boxes.xyxy.cpu().numpy()

        print(f"Image: {os.path.basename(image_path)}")
        print(f"Classes detected: {labels}")

        # Create a dictionary to store labels with their corresponding bounding boxes
        detected_objects = {}
        for label, box in zip(labels, boxes):
            if label not in detected_objects:
                detected_objects[label] = []
            detected_objects[label].append(box)

        return detected_objects


    def detect_direction(self,image_path):
        #load image
        original_image=cv2.imread(image_path)
        #veify if the image work
        if original_image is None:
            raise ValueError(f"Error to load the image {image_path}")

        # load YOLO on the image
        #Modelul YOLO este apelat cu imaginea ca intrare. Acesta efectuează detectarea obiectelor în imagine și returnează o listă de rezultate pentru fiecare cadru din imagine
        results = self.model(image_path)[0]

        # extract the directions
        #se foloseste .cpu(), pt ca tensorii lucreaza pe gpu, dar tu ai nevoie de cpu
        boxes = results.boxes.xyxy.cpu().numpy()
        #si convertește datele într-un array NumPy pentru a putea fi manipulate mai ușor  (.numpy())
        scores = results.boxes.conf.cpu().numpy()#Conține scorul de încredere (probabilitatea) pentru fiecare detecție YOLO
        labels = results.boxes.cls.cpu().numpy()#Conține indicele clasei fiecărui obiect detectat: 0:Front,1:Back, 2:Side

        print(f"Image: {os.path.basename(image_path)}")
        print(f"Classes detected: {labels}")

        # Variables for Front, Back and Side
        front_box, back_box, side_box = None, None, None

        #if he finds the classes for the model ex: 0:Front,1:Back, 2:Side
        for label, score, box in zip(labels, scores, boxes):
            if label == 0:  # Front
                front_box = box
                print(f"Front detected at: {front_box}")
            elif label == 1:  # Back
                back_box = box
                print(f"Back detected at: {back_box}")
            elif label == 2:  # Side
                side_box = box
                print(f"Side detected at: {side_box}")


         # Checks detected class combinations(will make a vector with those labels)
        detected_classes = set(labels)

        direction = None  #direction on witch is the car


        if detected_classes == {0, 1, 2}:  # all three
            if front_box is not None and back_box is not None and side_box is not None:
                if front_box[0] < back_box[0]:  # We compare the X coordinates
                    direction = "Left"
                elif front_box[0] > back_box[0]:
                    direction = "Right"

                print(f"Direction detected: {direction}")

        elif detected_classes == {0, 2}:  # Front și Side
            if front_box is not None and side_box is not None:
                if front_box[0] < side_box[0]:
                    direction = "Left"
                else:
                    direction = "Right"

                print(f"Direction detected: {direction}")

        elif detected_classes == {1, 2}:  # Back și Side
            if back_box is not None and side_box is not None:
                if back_box[0] > side_box[0]:
                    direction = "Left"
                else:
                    direction = "Right"

                print(f"Direction detected: {direction}")

        else:
            print(f"The image {os.path.basename(image_path)} It does NOT contain only Front and Side or Back and Side or all!")

        return direction

# Directorul scriptului .py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Calea relativă către fișierul model
model_path = os.path.join(BASE_DIR, "TrainedSets", "bestAngleCar.pt")

#verify if the model exists
if not os.path.exists(model_path):
    print(f"The model {model_path} has not find")
    exit()

# Creates the detector instance
detector = CarDirectionDetector(model_path)
print(f"The model {model_path} was load with succes!")


