import os
import cv2
import numpy as np
from ultralytics import YOLO




class CarElementsDetector:
    def __init__(self, model_path):
        # Verify if the model exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"The model {model_path} hasn't been found!")

        # Load the model only once
        self.model = YOLO(model_path)

    def detect_car(self, image_path):
        original_image = cv2.imread(image_path)
        if original_image is None:
            raise ValueError(f"Error loading the image {image_path}")

        # Run YOLO model on the image
        results = self.model(image_path)[0]

        # Extract bounding boxes, scores, and labels
        scores = results.boxes.conf.cpu().numpy()


        if len(scores) != 1:
            return False
        else:
            return True


    def draw_detections(self, image, box, label):
        if image is None:
            print("Eroare: imaginea este None!")
            return None
        print(f"Desenez: label={label}, box={box}")
        x_min, y_min, x_max, y_max = map(int, box)
        color = (0, 255, 0) if label == 0 else (0, 0, 255) if label == 1 else (255, 0, 0)
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color, 2)
        text = f""
        cv2.putText(image, text, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return image

    def detect_pillarsroof(self, image_path, angleDirection, classes,car_parts):
        # Load image
        original_image = cv2.imread(image_path)
        if original_image is None:
            raise ValueError(f"Error loading the image {image_path}")

        # Run YOLO model on the image
        results = self.model(image_path)[0]

        # Extract bounding boxes, scores, and labels
        boxes = results.boxes.xyxy.cpu().numpy()
        scores = results.boxes.conf.cpu().numpy()
        labels = results.boxes.cls.cpu().numpy()
        annotated_image1 = original_image.copy()


        print(f"Image: {os.path.basename(image_path)}")
        print(f"Classes detected: {labels}")

        detected_classes = set(classes.keys())
        print(f"Detected classes: {detected_classes}")
        print(f"Classes: {classes}")

        if len(scores) > 0:
            # max_score_index = np.argmax(scores)
            # best_label = labels[max_score_index]
            class_for_image=None
            this_zone = []
            if (0 in detected_classes and 1 in detected_classes and 2 in detected_classes) or (
                    0 in detected_classes and 1 not in detected_classes and 2 in detected_classes) or (
                    1 in detected_classes and 0 not in detected_classes and 2 in detected_classes):
                print("Intra in verificare")
                side_x_min, side_y_min, side_x_max, side_y_max = classes[2][0]
                class_for_image=classes[2][0]
                for box, label, score in zip(boxes, labels, scores):
                    x_min, y_min, x_max, y_max = box
                    print(f"Coordonate box: {x_min, y_min, x_max, y_max}")
                    print(f"Coordonate side: {side_x_min, side_y_min, side_x_max, side_y_max}")
                    if side_x_min-side_x_min/2 <= x_min <= side_x_max and side_x_min <= x_max <= side_x_max+side_x_max/2 and side_y_min <= y_max <= side_y_max:
                        print("S-a verificat")
                        this_zone.append((box, label, score))
            elif 0 in detected_classes and 1 not in detected_classes and 2 not in detected_classes:
                front_x_min, front_y_min, front_x_max, front_y_max = classes[0][0]
                class_for_image = classes[0][0]
                for box, label, score in zip(boxes, labels, scores):
                    x_min, y_min, x_max, y_max = box
                    if front_x_min <= x_min <= front_x_max and front_x_min <= x_max <= front_x_max and front_y_min <= y_max <= front_y_max:
                        this_zone.append((box, label, score))
            elif 0 not in detected_classes and 1 in detected_classes and 2 not in detected_classes:
                back_x_min, back_y_min, back_x_max, back_y_max = classes[1][0]
                class_for_image = classes[1][0]
                for box, label, score in zip(boxes, labels, scores):
                    x_min, y_min, x_max, y_max = box
                    if back_x_min <= x_min <= back_x_max and back_x_min <= x_max <= back_x_max and back_y_min <= y_max <= back_y_max:
                        this_zone.append((box, label, score))

            print(f"Zone: {this_zone}")
            if this_zone:
                # this_label = max(this_zone, key=lambda x: x[2])[1]
                this_box, this_label, this_score = max(this_zone, key=lambda x: x[2])
                if this_score > car_parts["PillarsRoof"].get("confidence", 0):
                    annotated_image = self.draw_detections(annotated_image1, this_box, this_label)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea!")
                    else:
                        print("Imaginea a fost adnotată corect.")
                    if this_label == 0:
                        car_parts["PillarsRoof"] = {"status": 0, "message": "Pillars and Roof No Problem", "confidence": this_score, "annotated_image": annotated_image}
                    elif this_label == 1:
                        car_parts["PillarsRoof"] = {"status": 1, "message": "Pillars and Roof Problem", "confidence": this_score, "annotated_image": annotated_image}
            elif car_parts["PillarsRoof"].get("confidence", -1) == -1:
                annotated_image = self.draw_detections(annotated_image1, class_for_image, 2)
                if annotated_image is None:
                    print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                else:
                    print("Imaginea a fost adnotată corect în caz de fallback.")
                car_parts["PillarsRoof"] = {"status": -1, "message": "No Pillars and Roof","confidence": 0, "annotated_image": annotated_image}


    def detect_wheel(self, image_path, angleDirection, classes,car_parts):
        # load image
        original_image = cv2.imread(image_path)
        # veify if the image work
        if original_image is None:
            raise ValueError(f"Error to load the image {image_path}")

        # load YOLO on the image
        # Modelul YOLO este apelat cu imaginea ca intrare.
        results = self.model(image_path)[0]

        # extract the directions
        # se foloseste .cpu(), pt ca tensorii lucreaza pe gpu, dar tu ai nevoie de cpu
        boxes = results.boxes.xyxy.cpu().numpy()
        # Acesta returnează coordonatele bounding box-urilor în format [x_min, y_min, x_max, y_max], unde:
        scores = results.boxes.conf.cpu().numpy()  # Conține scorul de încredere (probabilitatea) pentru fiecare detecție YOLO
        labels = results.boxes.cls.cpu().numpy()  # Conține indicele clasei fiecărui obiect detectat: 0:Front,1:Back, 2:Side

        print(f"Image: {os.path.basename(image_path)}")
        print(f"Classes detected: {labels}")

        annotated_image1 = original_image.copy()
        detected_classes = set(classes.keys())
        print(f"Detected classes: {detected_classes}")
        print(f"Classes: {classes}")
        # determina daca sunt elemente
        if len(scores) > 0:

            # verifica daca este in side
            if (0 in detected_classes and 1 in detected_classes and 2 in detected_classes) or (
                    0 in detected_classes and 1 not in detected_classes and 2 in detected_classes) or (
                    0 not in detected_classes and 1 in detected_classes and 2 in detected_classes):
                print("Intra in prima")
                side_x_min, side_y_min, side_x_max, side_y_max = classes[2][0]
                print(f"Coordonate front: {classes[2][0]}")
                front_zone = []
                back_zone = []
                side_mid_x = (side_x_min + side_x_max) / 2
                if angleDirection == "Right":
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if side_x_min <= x_min <= side_x_max and side_x_min <= x_max <= side_x_max and x_min >= side_mid_x and side_y_min <= y_min <= side_y_max:
                            front_zone.append((box, label, score))
                        elif side_x_min <= x_min <= side_x_max and side_x_min <= x_max <= side_x_max and x_max <= side_mid_x and side_y_min <= y_min <= side_y_max:
                            back_zone.append((box, label, score))
                elif angleDirection == "Left":
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if side_x_min <= x_min <= side_x_max and side_x_min <= x_max <= side_x_max and x_min >= side_mid_x and side_y_min <= y_min <= side_y_max:
                            back_zone.append((box, label, score))
                        elif side_x_min <= x_min <= side_x_max and side_x_min <= x_max <= side_x_max and x_max <= side_mid_x and side_y_min <= y_min <= side_y_max:
                            front_zone.append((box, label, score))
                print(f"Coordonate la prima:{front_zone}")
                print(f"Coordonate la a doua:{back_zone}")
                if angleDirection == "Right":
                    if front_zone:
                        # front_label = max(front_zone, key=lambda x: x[2])[1]
                        # front_label = max(front_zone, key=lambda x: x[2])[1]
                        front_box, front_label, front_score = max(front_zone, key=lambda x: x[2])
                        if front_score > car_parts["FrontRightWheel"].get("confidence", 0):
                            annotated_image = self.draw_detections(annotated_image1, front_box, front_label)
                            if annotated_image is None:
                                print("Eroare: Nu am reușit să adnotez imaginea!")
                            else:
                                print("Imaginea a fost adnotată corect.")
                            if front_label == 0:
                                car_parts["FrontRightWheel"] = {"status": 0, "message": "Front Right Wheel No Problem", "confidence": front_score, "annotated_image": annotated_image}
                            elif front_label == 1:
                                car_parts["FrontRightWheel"] = {"status": 1, "message": "Front Right Wheel Problem", "confidence": front_score, "annotated_image": annotated_image}
                            elif front_label == 2:
                                car_parts["FrontRightWheel"] = {"status": 2, "message": "No Front Right Wheel", "confidence": front_score, "annotated_image": annotated_image}
                    elif car_parts["FrontRightWheel"].get("confidence", -1) == -1:
                        annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                        else:
                            print("Imaginea a fost adnotată corect în caz de fallback.")

                        car_parts["FrontRightWheel"] = {"status": -1, "message": "No Front Right Wheel","confidence": 0, "annotated_image": annotated_image}


                    if back_zone:
                        back_box, back_label, back_score = max(back_zone, key=lambda x: x[2])
                        if back_score > car_parts["RearRightWheel"].get("confidence", 0):
                            annotated_image = self.draw_detections(annotated_image1, back_box, back_label)
                            if annotated_image is None:
                                print("Eroare: Nu am reușit să adnotez imaginea!")
                            else:
                                print("Imaginea a fost adnotată corect.")
                            if back_label == 0:
                                car_parts["RearRightWheel"] = {"status": 0, "message": "Back Right Wheel No Problem","confidence": back_score, "annotated_image": annotated_image}
                            elif back_label == 1:
                                car_parts["RearRightWheel"] = {"status": 1, "message": "Back Right Wheel Problem","confidence": back_score, "annotated_image": annotated_image}
                            elif back_label == 2:
                                car_parts["RearRightWheel"] = {"status": 2, "message": "No Back Right Wheel","confidence": back_score, "annotated_image": annotated_image}
                    elif car_parts["RearRightWheel"].get("confidence", -1) == -1:
                        annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                        else:
                            print("Imaginea a fost adnotată corect în caz de fallback.")
                        car_parts["RearRightWheel"] = {"status": -1, "message": "No Back Right Wheel", "confidence": 0, "annotated_image": annotated_image}

                elif angleDirection == "Left":

                    if front_zone:
                        # front_label = max(front_zone, key=lambda x: x[2])[1]
                        front_box, front_label, front_score = max(front_zone, key=lambda x: x[2])
                        if front_score > car_parts["FrontLeftWheel"].get("confidence", 0):
                            annotated_image = self.draw_detections(annotated_image1, front_box, front_label)
                            if annotated_image is None:
                                print("Eroare: Nu am reușit să adnotez imaginea!")
                            else:
                                print("Imaginea a fost adnotată corect.")
                            if front_label == 0:
                                car_parts["FrontLeftWheel"] = {"status": 0, "message": "Front Left Wheel No Problem", "confidence": front_score, "annotated_image": annotated_image}
                            elif front_label == 1:
                                car_parts["FrontLeftWheel"] = {"status": 1, "message": "Front Left Wheel Problem", "confidence": front_score, "annotated_image": annotated_image}
                            elif front_label == 2:
                                car_parts["FrontLeftWheel"] = {"status": 2, "message": "No Front Left Wheel", "confidence": front_score, "annotated_image": annotated_image}
                    elif car_parts["FrontLeftWheel"].get("confidence", -1) == -1:
                        annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                        else:
                            print("Imaginea a fost adnotată corect în caz de fallback.")
                        car_parts["FrontLeftWheel"] = {"status": -1, "message": "No Front Left Wheel", "confidence": 0, "annotated_image": annotated_image}


                    if back_zone:
                        # back_label = max(back_zone, key=lambda x: x[2])[1]
                        back_box, back_label, back_score = max(back_zone, key=lambda x: x[2])
                        if back_score > car_parts["RearLeftWheel"].get("confidence", 0):
                            annotated_image = self.draw_detections(annotated_image1, back_box, back_label)
                            if annotated_image is None:
                                print("Eroare: Nu am reușit să adnotez imaginea!")
                            else:
                                print("Imaginea a fost adnotată corect.")
                            if back_label == 0:
                                car_parts["RearLeftWheel"] = {"status": 0, "message": "Back Left Wheel No Problem","confidence": back_score, "annotated_image": annotated_image}
                            elif back_label == 1:
                                car_parts["RearLeftWheel"] = {"status": 1, "message": "Back Left Wheel Problem","confidence": back_score, "annotated_image": annotated_image}
                            elif back_label == 1:
                                car_parts["RearLeftWheel"] = {"status": 2, "message": "No Back Left Wheel","confidence": back_score, "annotated_image": annotated_image}
                    elif car_parts["RearLeftWheel"].get("confidence", -1) == -1:
                        annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                        else:
                            print("Imaginea a fost adnotată corect în caz de fallback.")
                        car_parts["RearLeftWheel"] = {"status": -1, "message": "No Back Left Wheel", "confidence": 0, "annotated_image": annotated_image}



#Trebuie verificat sa nu se mai intre in executari in cazul in care lipseste ceva!!!!
    def detect_window(self, image_path, angleDirection, classes,car_parts):  # trb facut si pentru cazu in care nu este usa
        # load image
        original_image = cv2.imread(image_path)
        # veify if the image work
        if original_image is None:
            raise ValueError(f"Error to load the image {image_path}")

        # load YOLO on the image
        # Modelul YOLO este apelat cu imaginea ca intrare.
        results = self.model(image_path)[0]

        # extract the directions
        # se foloseste .cpu(), pt ca tensorii lucreaza pe gpu, dar tu ai nevoie de cpu
        boxes = results.boxes.xyxy.cpu().numpy()
        # Acesta returnează coordonatele bounding box-urilor în format [x_min, y_min, x_max, y_max], unde:
        scores = results.boxes.conf.cpu().numpy()  # Conține scorul de încredere (probabilitatea) pentru fiecare detecție YOLO
        labels = results.boxes.cls.cpu().numpy()  # Conține indicele clasei fiecărui obiect detectat: 0:Front,1:Back, 2:Side

        print(f"Image: {os.path.basename(image_path)}")
        print(f"Classes detected: {labels}")

        annotated_image1 = original_image.copy()

        detected_classes = set(classes.keys())
        print(f"Detected classes: {detected_classes}")
        print(f"Classes: {classes}")
        # determina daca sunt elemente
        if len(scores) > 0:

            # verifica daca este in side
            if (0 in detected_classes and 1 in detected_classes and 2 in detected_classes) or (
                    0 in detected_classes and 1 not in detected_classes and 2 in detected_classes) or (
                    0 not in detected_classes and 1 in detected_classes and 2 in detected_classes):
                print("Intra in prima")
                side_x_min, side_y_min, side_x_max, side_y_max = classes[2][0]
                print(f"Coordonate front: {classes[2][0]}")

                front_zone = []
                back_zone = []
                if len(boxes) == 1:
                    x_min, y_min, x_max, y_max = boxes[0]
                    side_mid_x = (side_x_min + side_x_max) / 2
                    if side_x_min <= x_min <= side_x_max and side_x_min <= x_max <= side_x_max and x_min - x_min / 4 <= side_mid_x <= x_max + x_max / 4 and side_y_min <= y_max <= side_y_max:
                        front_zone.append((boxes[0], labels[0], scores[0]))
                elif len(boxes) == 2:
                    print("Intra la a doua")
                    x1_min, y1_min, x1_max, y1_max = boxes[0]
                    print(f"Coordonate la prima:{boxes[0]}")
                    print(f"Coordonate la prima:{x1_min, y1_min, x1_max, y1_max}")
                    x2_min, y2_min, x2_max, y2_max = boxes[1]
                    print(f"Coordonate la a doua:{boxes[1]}")
                    print(f"Coordonate la a doua:{x2_min, y2_min, x2_max, y2_max}")
                    if angleDirection == "Right":
                        if x1_min > x2_min:
                            if side_x_min <= x1_min <= side_x_max and side_x_min <= x1_max <= side_x_max and side_y_min <= y1_max <= side_y_max:
                                front_zone.append((boxes[0], labels[0], scores[0]))
                            if side_x_min <= x2_min <= side_x_max and side_x_min <= x2_max <= side_x_max and side_y_min <= y2_max <= side_y_max:
                                back_zone.append((boxes[1], labels[1], scores[1]))
                        elif x1_min < x2_min:
                            if side_x_min <= x2_min <= side_x_max and side_x_min <= x2_max <= side_x_max and side_y_min <= y2_max <= side_y_max:
                                front_zone.append((boxes[1], labels[1], scores[1]))
                            if side_x_min <= x1_min <= side_x_max and side_x_min <= x1_max <= side_x_max and side_y_min <= y1_max <= side_y_max:
                                back_zone.append((boxes[0], labels[0], scores[0]))
                    elif angleDirection == "Left":
                        if x1_min > x2_min:
                            if side_x_min <= x2_min <= side_x_max and side_x_min <= x2_max <= side_x_max and side_y_min <= y2_max <= side_y_max:
                                front_zone.append((boxes[1], labels[1], scores[1]))
                            if side_x_min <= x1_min <= side_x_max and side_x_min <= x1_max <= side_x_max and side_y_min <= y1_max <= side_y_max:
                                back_zone.append((boxes[0], labels[0], scores[0]))
                        elif x1_min < x2_min:
                            if side_x_min <= x1_min <= side_x_max and side_x_min <= x1_max <= side_x_max and side_y_min <= y1_max <= side_y_max:
                                front_zone.append((boxes[0], labels[0], scores[0]))
                            if side_x_min <= x2_min <= side_x_max and side_x_min <= x2_max <= side_x_max and side_y_min <= y2_max <= side_y_max:
                                back_zone.append((boxes[1], labels[1], scores[1]))
                elif len(boxes) > 2:
                    sorted_boxes = sorted(boxes, key=lambda box: abs(box[0] - side_x_min))
                    box1, box2 = sorted_boxes[0], sorted_boxes[-1]

                    x1_min, y1_min, x1_max, y1_max = box1
                    x2_min, y2_min, x2_max, y2_max = box2
                    if angleDirection == "Right":
                        # Clasifică obiectele în funcție de poziție și reține box, label și score
                        for box, label, score in zip(boxes, labels, scores):
                            x_min, y_min, x_max, y_max = box
                            if x2_min == x_min and side_x_min <= x_min <= side_x_max and side_x_min <= x_max <= side_x_max and side_y_min <= y_max <= side_y_max:
                                print(f"Box {box} added to back_zone")
                                front_zone.append((box, label, score))
                            elif x1_min == x_min and side_x_min <= x_min <= side_x_max and side_x_min <= x_max <= side_x_max and side_y_min <= y_max <= side_y_max:
                                print(f"Box {box} added to back_zone")
                                back_zone.append((box, label, score))
                    elif angleDirection == "Left":
                        # Clasifică obiectele în funcție de poziție și reține box, label și score
                        for box, label, score in zip(boxes, labels, scores):
                            x_min, y_min, x_max, y_max = box
                            if x1_min == x_min and side_x_min <= x_min <= side_x_max and side_x_min <= x_max <= side_x_max and side_y_min <= y_max <= side_y_max:
                                print(f"Box {box} added to back_zone")
                                front_zone.append((box, label, score))
                            elif x2_min == x_min and side_x_min <= x_min <= side_x_max and side_x_min <= x_max <= side_x_max and side_y_min <= y_max <= side_y_max:
                                print(f"Box {box} added to back_zone")
                                back_zone.append((box, label, score))

                if angleDirection == "Right":
                    if car_parts.get("FrontRightDoor", {}).get("status") in [2, -1]:
                        car_parts["FrontRightWindow"] = {"status": 2, "message": "No Front Right Window"}
                    else:
                        if front_zone:
                            # front_label = front_zone[0][1]
                            # front_label = max(front_zone, key=lambda x: x[2])[1]
                            front_box, front_label, front_score = max(front_zone, key=lambda x: x[2])
                            if front_score > car_parts["FrontRightWindow"].get("confidence", 0):
                                annotated_image = self.draw_detections(annotated_image1, front_box, front_label)
                                if annotated_image is None:
                                    print("Eroare: Nu am reușit să adnotez imaginea!")
                                else:
                                    print("Imaginea a fost adnotată corect.")

                                if front_label == 0:
                                    car_parts["FrontRightWindow"] = {"status": 0, "message": "Front Right Window No Problem", "confidence": front_score, "annotated_image": annotated_image}
                                elif front_label == 1:
                                    car_parts["FrontRightWindow"] = {"status": 1, "message": "Front Right Window Problem", "confidence": front_score, "annotated_image": annotated_image}
                                elif front_label == 2:
                                    car_parts["FrontRightWindow"] = {"status": 2, "message": "No Front Right Window", "confidence": front_score, "annotated_image": annotated_image}

                    print(f"Dimensiune back_zone{back_zone}")
                    if car_parts.get("RearRightDoor", {}).get("status") in [2, -1]:
                        car_parts["RearRightWindow"] = {"status": 2, "message": "No Back Right Window"}
                    else:

                        if back_zone:
                            back_box, back_label, back_score = max(back_zone, key=lambda x: x[2])
                            if back_score > car_parts["RearRightWindow"].get("confidence", 0):
                                annotated_image = self.draw_detections(annotated_image1, back_box, back_label)
                                if annotated_image is None:
                                    print("Eroare: Nu am reușit să adnotez imaginea!")
                                else:
                                    print("Imaginea a fost adnotată corect.")

                                if back_label == 0:
                                    car_parts["RearRightWindow"] = {"status": 0, "message": "Back Right Window No Problem", "confidence": back_score, "annotated_image": annotated_image}
                                elif back_label == 1:
                                    car_parts["RearRightWindow"] = {"status": 1, "message": "Back Right Window Problem", "confidence": back_score, "annotated_image": annotated_image}
                                elif back_label == 2:
                                    car_parts["RearRightWindow"] = {"status": 2, "message": "No Back Right Window", "confidence": back_score, "annotated_image": annotated_image}

                elif angleDirection == "Left":
                    if car_parts.get("FrontLeftDoor", {}).get("status") in [2, -1]:
                        car_parts["FrontLeftWindow"] = {"status": 2, "message": "No Front Left Window"}
                    else:

                        if front_zone:
                            #front_label = front_zone[0][1]
                            # front_label = max(front_zone, key=lambda x: x[2])[1]
                            front_box, front_label, front_score = max(front_zone, key=lambda x: x[2])
                            if front_score > car_parts["FrontLeftWindow"].get("confidence", 0):
                                annotated_image = self.draw_detections(annotated_image1, front_box, front_label)
                                if annotated_image is None:
                                    print("Eroare: Nu am reușit să adnotez imaginea!")
                                else:
                                    print("Imaginea a fost adnotată corect.")
                                if front_label == 0:
                                    car_parts["FrontLeftWindow"] = {"status": 0, "message": "Front Left Window No Problem", "confidence": front_score, "annotated_image": annotated_image}
                                elif front_label == 1:
                                    car_parts["FrontLeftWindow"] = {"status": 1, "message": "Front Left Window Problem", "confidence": front_score, "annotated_image": annotated_image}
                                elif front_label == 2:
                                    car_parts["FrontLeftWindow"] = {"status": 2, "message": "No Front Left Window", "confidence": front_score, "annotated_image": annotated_image}

                    print(f"Dimensiune back_zone{back_zone}")
                    if car_parts.get("RearLeftDoor", {}).get("status") in [2, -1]:
                        car_parts["RearLeftWindow"] = {"status": 2, "message": "No Back Left Window"}
                    else:

                        if back_zone:

                            back_box, back_label, back_score = max(back_zone, key=lambda x: x[2])
                            if back_score > car_parts["RearLeftWindow"].get("confidence", 0):
                                annotated_image = self.draw_detections(annotated_image1, back_box, back_label)
                                if annotated_image is None:
                                    print("Eroare: Nu am reușit să adnotez imaginea!")
                                else:
                                    print("Imaginea a fost adnotată corect.")
                                if back_label == 0:
                                    car_parts["RearLeftWindow"] = {"status": 0, "message": "Back Left Window No Problem", "confidence": back_score, "annotated_image": annotated_image}
                                elif back_label == 1:
                                    car_parts["RearLeftWindow"] = {"status": 1, "message": "Back Left Window Problem", "confidence": back_score, "annotated_image": annotated_image}
                                elif back_label == 2:
                                    car_parts["RearLeftWindow"] = {"status": 2, "message": "No Back Left Window", "confidence": back_score, "annotated_image": annotated_image}


    def detect_door(self, image_path, angleDirection, classes,car_parts):
        # load image
        original_image = cv2.imread(image_path)
        # veify if the image work
        if original_image is None:
            raise ValueError(f"Error to load the image {image_path}")

        # load YOLO on the image
        # Modelul YOLO este apelat cu imaginea ca intrare.
        results = self.model(image_path)[0]

        # extract the directions
        # se foloseste .cpu(), pt ca tensorii lucreaza pe gpu, dar tu ai nevoie de cpu
        boxes = results.boxes.xyxy.cpu().numpy()
        # Acesta returnează coordonatele bounding box-urilor în format [x_min, y_min, x_max, y_max], unde:
        scores = results.boxes.conf.cpu().numpy()  # Conține scorul de încredere (probabilitatea) pentru fiecare detecție YOLO
        labels = results.boxes.cls.cpu().numpy()  # Conține indicele clasei fiecărui obiect detectat: 0:Front,1:Back, 2:Side

        print(f"Image: {os.path.basename(image_path)}")
        print(f"Classes detected: {labels}")

        annotated_image1 = original_image.copy()

        detected_classes = set(classes.keys())
        print(f"Detected classes: {detected_classes}")
        print(f"Classes: {classes}")
        # determina daca sunt elemente
        if len(scores) > 0:

            # verifica daca este in side
            if (0 in detected_classes and 1 in detected_classes and 2 in detected_classes) or (0 in detected_classes and 1 not in detected_classes and 2 in detected_classes) or (0 not in detected_classes and 1 in detected_classes and 2 in detected_classes):
                print("Intra in prima")
                side_x_min, side_y_min, side_x_max, side_y_max = classes[2][0]
                print(f"Coordonate front: {classes[2][0]}")

                front_zone = []
                back_zone = []
                print(f"Numărul de bounding boxes detectate: {len(boxes)}")
                print(f"Coordonate bounding boxes: {boxes}")
                if len(boxes) == 1:
                    x_min, y_min, x_max, y_max = boxes[0]
                    side_mid_x = (side_x_min + side_x_max) / 2
                    if side_x_min <= x_min <= side_x_max and side_x_min <= x_max <= side_x_max and x_min-x_min/4<=side_mid_x<=x_max+x_max/4 and side_y_min <= y_max <= side_y_max:
                        front_zone.append((boxes[0], labels[0], scores[0]))
                elif len(boxes) == 2:
                    print("Intra la a doua")
                    x1_min, y1_min, x1_max, y1_max = boxes[0]
                    print(f"Coordonate la prima:{boxes[0]}")
                    print(f"Coordonate la prima:{x1_min, y1_min, x1_max, y1_max}")
                    x2_min, y2_min, x2_max, y2_max = boxes[1]
                    print(f"Coordonate la a doua:{boxes[1]}")
                    print(f"Coordonate la a doua:{x2_min, y2_min, x2_max, y2_max}")
                    if angleDirection == "Right":
                        if x1_min >= x2_min:
                            if side_x_min <= x1_min <= side_x_max and side_x_min <= x1_max <= side_x_max and side_y_min <= y1_max <= side_y_max:
                                front_zone.append((boxes[0], labels[0], scores[0]))
                            if side_x_min <= x2_min <= side_x_max and side_x_min <= x2_max <= side_x_max and side_y_min <= y2_max <= side_y_max:
                                back_zone.append((boxes[1], labels[1], scores[1]))
                        elif x1_min < x2_min:
                            if side_x_min <= x2_min <= side_x_max and side_x_min <= x2_max <= side_x_max and side_y_min <= y2_max <= side_y_max:
                                front_zone.append((boxes[1], labels[1], scores[1]))
                            if side_x_min <= x1_min <= side_x_max and side_x_min <= x1_max <= side_x_max and side_y_min <= y1_max <= side_y_max:
                                back_zone.append((boxes[0], labels[0], scores[0]))
                    elif angleDirection == "Left":
                        if x1_min >= x2_min:
                            if side_x_min <= x2_min <= side_x_max and side_x_min <= x2_max <= side_x_max and side_y_min <= y2_max <= side_y_max:
                                front_zone.append((boxes[1], labels[1], scores[1]))
                            if side_x_min <= x1_min <= side_x_max and side_x_min <= x1_max <= side_x_max and side_y_min <= y1_max <= side_y_max:
                                back_zone.append((boxes[0], labels[0], scores[0]))
                        elif x1_min < x2_min:
                            if side_x_min <= x1_min <= side_x_max and side_x_min <= x1_max <= side_x_max and side_y_min <= y1_max <= side_y_max:
                                front_zone.append((boxes[0], labels[0], scores[0]))
                            if side_x_min <= x2_min <= side_x_max and side_x_min <= x2_max <= side_x_max and side_y_min <= y2_max <= side_y_max:
                                back_zone.append((boxes[1], labels[1], scores[1]))
                    print(f"Front zone:{front_zone}")
                    print(f"Back zone: {back_zone}")
                elif len(boxes) > 2:
                    sorted_boxes = sorted(boxes, key=lambda box: abs(box[0] - side_x_min))
                    box1, box2 = sorted_boxes[0], sorted_boxes[-1]

                    x1_min, y1_min, x1_max, y1_max = box1
                    x2_min, y2_min, x2_max, y2_max = box2
                    if angleDirection == "Right":
                        # Clasifică obiectele în funcție de poziție și reține box, label și score
                        for box, label, score in zip(boxes, labels, scores):
                            x_min, y_min, x_max, y_max = box
                            if x2_min == x_min and side_x_min <= x_min <= side_x_max and side_x_min <= x_max <= side_x_max and side_y_min <= y_max <= side_y_max:
                                print(f"Box {box} added to back_zone")
                                front_zone.append((box, label, score))
                            elif x1_min == x_min and side_x_min <= x_min <= side_x_max and side_x_min <= x_max <= side_x_max and side_y_min <= y_max <= side_y_max:
                                print(f"Box {box} added to back_zone")
                                back_zone.append((box, label, score))
                    elif angleDirection == "Left":
                        # Clasifică obiectele în funcție de poziție și reține box, label și score
                        for box, label, score in zip(boxes, labels, scores):
                            x_min, y_min, x_max, y_max = box
                            if x1_min == x_min and side_x_min <= x_min <= side_x_max and side_x_min <= x_max <= side_x_max and side_y_min <= y_max <= side_y_max:
                                print(f"Box {box} added to back_zone")
                                front_zone.append((box, label, score))
                            elif x2_min == x_min and side_x_min <= x_min <= side_x_max and side_x_min <= x_max <= side_x_max and side_y_min <= y_max <= side_y_max:
                                print(f"Box {box} added to back_zone")
                                back_zone.append((box, label, score))

                if angleDirection == "Right":
                    if front_zone:
                        #front_label = front_zone[0][1]
                        # front_label = max(front_zone, key=lambda x: x[2])[1]
                        front_box, front_label, front_score = max(front_zone, key=lambda x: x[2])
                        if front_score > car_parts["FrontRightDoor"].get("confidence", 0):
                            annotated_image = self.draw_detections(annotated_image1, front_box, front_label)
                            if annotated_image is None:
                                print("Eroare: Nu am reușit să adnotez imaginea!")
                            else:
                                print("Imaginea a fost adnotată corect.")
                            if front_label == 0:
                                car_parts["FrontRightDoor"] = {"status": 0, "message": "Front Right Door No Problem", "confidence": front_score, "annotated_image": annotated_image}
                            elif front_label == 1:
                                car_parts["FrontRightDoor"] = {"status": 1, "message": "Front Right Door Problem", "confidence": front_score, "annotated_image": annotated_image}
                            elif front_label == 2:
                                car_parts["FrontRightDoor"] = {"status": 2, "message": "No Front Right Door", "confidence": front_score, "annotated_image": annotated_image}
                    print(f"Dimensiune back_zone{back_zone}")

                    if back_zone:
                        #back_label = back_zone[0][1]
                        # back_label = max(back_zone, key=lambda x: x[2])[1]
                        back_box, back_label, back_score = max(back_zone, key=lambda x: x[2])
                        if back_score > car_parts["RearRightDoor"].get("confidence", 0):
                            annotated_image = self.draw_detections(annotated_image1, back_box, back_label)
                            if annotated_image is None:
                                print("Eroare: Nu am reușit să adnotez imaginea!")
                            else:
                                print("Imaginea a fost adnotată corect.")

                            if back_label == 0:
                                car_parts["RearRightDoor"] = {"status": 0, "message": "Back Right Door No Problem", "confidence": back_score, "annotated_image": annotated_image}
                            elif back_label == 1:
                                car_parts["RearRightDoor"] = {"status": 1, "message": "Back Right Door Problem", "confidence": back_score, "annotated_image": annotated_image}
                            elif back_label == 2:
                                car_parts["RearRightDoor"] = {"status": 2, "message": "No Back Right Door", "confidence": back_score, "annotated_image": annotated_image}
                elif angleDirection == "Left":
                    if front_zone:
                        #front_label = front_zone[0][1]
                        # front_label = max(front_zone, key=lambda x: x[2])[1]
                        front_box, front_label, front_score = max(front_zone, key=lambda x: x[2])
                        if front_score > car_parts["FrontLeftDoor"].get("confidence", 0):
                            annotated_image = self.draw_detections(annotated_image1, front_box, front_label)
                            if annotated_image is None:
                                print("Eroare: Nu am reușit să adnotez imaginea!")
                            else:
                                print("Imaginea a fost adnotată corect.")
                            if front_label == 0:
                                car_parts["FrontLeftDoor"] = {"status": 0, "message": "Front Left Door No Problem", "confidence": front_score, "annotated_image": annotated_image}
                            elif front_label == 1:
                                car_parts["FrontLeftDoor"] = {"status": 1, "message": "Front Left Door Problem", "confidence": front_score, "annotated_image": annotated_image}
                            elif front_label == 2:
                                car_parts["FrontLeftDoor"] = {"status": 2, "message": "No Front Left Door", "confidence": front_score, "annotated_image": annotated_image}

                    if back_zone:
                        #back_label = back_zone[0][1]
                        # back_label = max(back_zone, key=lambda x: x[2])[1]
                        back_box, back_label, back_score = max(back_zone, key=lambda x: x[2])
                        if back_score > car_parts["RearLeftDoor"].get("confidence", 0):
                            annotated_image = self.draw_detections(annotated_image1, back_box, back_label)
                            if annotated_image is None:
                                print("Eroare: Nu am reușit să adnotez imaginea!")
                            else:
                                print("Imaginea a fost adnotată corect.")

                            if back_label == 0:
                                car_parts["RearLeftDoor"] = {"status": 0, "message": "Back Left Door No Problem", "confidence": back_score, "annotated_image": annotated_image}
                            elif back_label == 1:
                                car_parts["RearLeftDoor"] = {"status": 1, "message": "Back Left Door Problem", "confidence": back_score, "annotated_image": annotated_image}
                            elif back_label == 2:
                                car_parts["RearLeftDoor"] = {"status": 2, "message": "No Back Left Door", "confidence": back_score, "annotated_image": annotated_image}


    def detect_mirror(self, image_path, angleDirection, classes,car_parts):
        # load image
        original_image = cv2.imread(image_path)
        # veify if the image work
        if original_image is None:
            raise ValueError(f"Error to load the image {image_path}")

        # load YOLO on the image
        # Modelul YOLO este apelat cu imaginea ca intrare.
        results = self.model(image_path)[0]

        # extract the directions
        # se foloseste .cpu(), pt ca tensorii lucreaza pe gpu, dar tu ai nevoie de cpu
        boxes = results.boxes.xyxy.cpu().numpy()
        # Acesta returnează coordonatele bounding box-urilor în format [x_min, y_min, x_max, y_max], unde:
        scores = results.boxes.conf.cpu().numpy()  # Conține scorul de încredere (probabilitatea) pentru fiecare detecție YOLO
        labels = results.boxes.cls.cpu().numpy()  # Conține indicele clasei fiecărui obiect detectat: 0:Front,1:Back, 2:Side

        print(f"Image: {os.path.basename(image_path)}")
        print(f"Classes detected: {labels}")


        # Checks detected class combinations(will make a vector with those labels)
        # detected_classes = set(labels)

        detected_classes = set(classes.keys())
        print(f"Detected classes: {detected_classes}")
        print(f"Classes: {classes}")
        # determina daca sunt elemente
        annotated_image1 = original_image.copy()

        if len(scores) > 0:

            # verifica daca este in side
            if 0 in detected_classes and 1 not in detected_classes and 2 not in detected_classes:

                print("Intra in prima")
                front_x_min, front_y_min, front_x_max, front_y_max = classes[0][0]
                print(f"Coordonate front: {classes[0][0]}")

                front_mid_x = (front_x_min + front_x_max) / 2  # Calculăm mijlocul zonei front

                right_zone = []
                left_zone = []

                # Clasifică obiectele în funcție de poziție și reține box, label și score
                for box, label, score in zip(boxes, labels, scores):
                    x_min, y_min, x_max, y_max = box

                    if front_y_min <= y_min <= front_y_max:
                        if x_max <= front_mid_x:  # Obiectul este în jumătatea stângă
                            print(f"Box {box} added to right_zone")
                            right_zone.append((box, label, score))
                        elif x_min >= front_mid_x:  # Obiectul este în jumătatea dreaptă
                            print(f"Box {box} added to left_zone")
                            left_zone.append((box, label, score))


                if right_zone:
                    # right_label = max(right_zone, key=lambda x: x[2])[1]
                    right_box, right_label, right_score = max(right_zone, key=lambda x: x[2])
                    if right_score > car_parts["RightMirror"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, right_box, right_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")

                        if right_label == 0:
                            car_parts["RightMirror"] = {"status": 0, "message": "Right Mirror No Problem", "confidence": right_score, "annotated_image": annotated_image}
                        elif right_label == 1:
                            car_parts["RightMirror"] = {"status": 1, "message": "Right Mirror Problem", "confidence": right_score, "annotated_image": annotated_image}
                        elif right_label == 2:
                            car_parts["RightMirror"] = {"status": 2, "message": "No Right Mirror", "confidence": right_score, "annotated_image": annotated_image}
                elif car_parts["RightMirror"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")

                    car_parts["RightMirror"] = {"status": -1, "message": "No Right Mirror", "confidence": 0, "annotated_image": annotated_image}


                if left_zone:
                    # left_label = max(left_zone, key=lambda x: x[2])[1]
                    left_box, left_label, left_score = max(left_zone, key=lambda x: x[2])
                    if left_score > car_parts["LeftMirror"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, left_box, left_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")
                        if left_label == 0:
                            car_parts["LeftMirror"] = {"status": 0, "message": "Left Mirror No Problem", "confidence": left_score, "annotated_image": annotated_image}
                        elif left_label == 1:
                            car_parts["LeftMirror"] = {"status": 1, "message": "Left Mirror Problem", "confidence": left_score, "annotated_image": annotated_image}
                        elif left_label == 2:
                            car_parts["LeftMirror"] = {"status": 2, "message": "No Left Mirror", "confidence": left_score, "annotated_image": annotated_image}
                elif car_parts["LeftMirror"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")

                    car_parts["LeftMirror"] = {"status": -1, "message": "No Left Mirror", "confidence": 0, "annotated_image": annotated_image}


            elif (0 in detected_classes and 1 in detected_classes and 2 in detected_classes) or (
                    0 in detected_classes and 1 not in detected_classes and 2 in detected_classes) or(
                    0 not in detected_classes and 1 in detected_classes and 2 in detected_classes):
                print("Intra in a doua")
                front_x_min, front_y_min, front_x_max, front_y_max = classes[2][0]
                print(f"Coordonate front: {classes[2][0]}")
                front_mid_x = (front_x_min + front_x_max) / 2

                if angleDirection == "Right":
                    right_zone = []
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if front_mid_x-front_mid_x/3 <= x_min <= front_x_max and front_y_min <= y_min <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            right_zone.append((box, label, score))
                    if right_zone:
                        # right_label = max(right_zone, key=lambda x: x[2])[1]
                        right_box, right_label, right_score = max(right_zone, key=lambda x: x[2])
                        if right_score > car_parts["RightMirror"].get("confidence", 0):
                            annotated_image = self.draw_detections(annotated_image1, right_box, right_label)
                            if annotated_image is None:
                                print("Eroare: Nu am reușit să adnotez imaginea!")
                            else:
                                print("Imaginea a fost adnotată corect.")

                            if right_label == 0:
                                car_parts["RightMirror"] = {"status": 0, "message": "Right Mirror No Problem",
                                                            "confidence": right_score,
                                                            "annotated_image": annotated_image}
                            elif right_label == 1:
                                car_parts["RightMirror"] = {"status": 1, "message": "Right Mirror Problem",
                                                            "confidence": right_score,
                                                            "annotated_image": annotated_image}
                            elif right_label == 2:
                                car_parts["RightMirror"] = {"status": 2, "message": "No Right Mirror",
                                                            "confidence": right_score,
                                                            "annotated_image": annotated_image}
                    elif car_parts["RightMirror"].get("confidence", -1) == -1:
                        annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                        else:
                            print("Imaginea a fost adnotată corect în caz de fallback.")

                        car_parts["RightMirror"] = {"status": -1, "message": "No Right Mirror", "confidence": 0,
                                                    "annotated_image": annotated_image}
                elif angleDirection == "Left":
                    left_zone = []

                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if front_x_min <= x_max <= front_mid_x+front_mid_x/3 and front_y_min <= y_min <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            left_zone.append((box, label, score))

                    best_box, best_label, best_score = max(left_zone, key=lambda x: x[2])  # Selectăm elementul cu cel mai mare scor

                    if left_zone:
                        # left_label = max(left_zone, key=lambda x: x[2])[1]
                        left_box, left_label, left_score = max(left_zone, key=lambda x: x[2])
                        if left_score > car_parts["LeftMirror"].get("confidence", 0):
                            annotated_image = self.draw_detections(annotated_image1, left_box, left_label)
                            if annotated_image is None:
                                print("Eroare: Nu am reușit să adnotez imaginea!")
                            else:
                                print("Imaginea a fost adnotată corect.")
                            if left_label == 0:
                                car_parts["LeftMirror"] = {"status": 0, "message": "Left Mirror No Problem",
                                                           "confidence": left_score, "annotated_image": annotated_image}
                            elif left_label == 1:
                                car_parts["LeftMirror"] = {"status": 1, "message": "Left Mirror Problem",
                                                           "confidence": left_score, "annotated_image": annotated_image}
                            elif left_label == 2:
                                car_parts["LeftMirror"] = {"status": 2, "message": "No Left Mirror",
                                                           "confidence": left_score, "annotated_image": annotated_image}
                    elif car_parts["LeftMirror"].get("confidence", -1) == -1:
                        annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                        else:
                            print("Imaginea a fost adnotată corect în caz de fallback.")

                        car_parts["LeftMirror"] = {"status": -1, "message": "No Left Mirror", "confidence": 0,
                                                   "annotated_image": annotated_image}

    def detect_windshieldrearwindow(self, image_path, angleDirection, classes,car_parts):
        #load image
        original_image=cv2.imread(image_path)
        #veify if the image work
        if original_image is None:
            raise ValueError(f"Error to load the image {image_path}")

        # load YOLO on the image
        #Modelul YOLO este apelat cu imaginea ca intrare.
        results = self.model(image_path)[0]

        # extract the directions
        #se foloseste .cpu(), pt ca tensorii lucreaza pe gpu, dar tu ai nevoie de cpu
        boxes = results.boxes.xyxy.cpu().numpy()
        #Acesta returnează coordonatele bounding box-urilor în format [x_min, y_min, x_max, y_max], unde:
        scores = results.boxes.conf.cpu().numpy()#Conține scorul de încredere (probabilitatea) pentru fiecare detecție YOLO
        labels = results.boxes.cls.cpu().numpy()#Conține indicele clasei fiecărui obiect detectat: 0:Front,1:Back, 2:Side

        print(f"Image: {os.path.basename(image_path)}")
        print(f"Classes detected: {labels}")

        # Variables for Front, Back and Side

        annotated_image1 = original_image.copy()

        detected_classes = set(classes.keys())
        print(f"Detected classes: {detected_classes}")
        print(f"Classes: {classes}")
        # determina daca sunt elemente
        if len(scores) > 0:
            if 0 in detected_classes and 1 not in detected_classes and 2 in detected_classes:
                print("Intra in a doua")
                front_x_min, front_y_min, front_x_max, front_y_max = classes[2][0]
                front_mid_x = (front_x_min + front_x_max) / 2
                print(f"Coordonate front: {classes[0][0]}")
                front_zone = []
                if angleDirection == "Right":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        print(f"Box {box} added to back_zone")
                        if front_mid_x - front_mid_x / 4 <= x_min <= front_x_max and front_y_min <= y_max <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            front_zone.append((box, label, score))
                elif angleDirection == "Left":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        print(f"Box {box} added to back_zone")
                        if front_x_min <= x_max <= front_mid_x + front_mid_x / 4 and front_y_min <= y_max <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            front_zone.append((box, label, score))
                print(f"Front zone: {front_zone}")


                if front_zone:
                    #best_label = max(front_zone, key=lambda x: x[2])[1]
                    # front_label = max(front_zone, key=lambda x: x[2])[1]
                    front_box, front_label, front_score = max(front_zone, key=lambda x: x[2])
                    if front_score > car_parts["Windshield"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, front_box, front_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")

                        if front_label == 0:
                            car_parts["Windshield"] = {"status": 0, "message": "Windshield No Problem", "confidence": front_score, "annotated_image": annotated_image}
                        elif front_label == 1:
                            car_parts["Windshield"] = {"status": 1, "message": "Windshield Problem","confidence": front_score, "annotated_image": annotated_image}
                        elif front_label == 2:
                            car_parts["Windshield"] = {"status": 2, "message": "No Windshield","confidence": front_score, "annotated_image": annotated_image}
                elif car_parts["Windshield"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[2][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")

                    car_parts["Windshield"] = {"status": -1, "message": "No Windshield","confidence": 0, "annotated_image": annotated_image}

            elif 0 in detected_classes and 1 not in detected_classes and 2 not in detected_classes:
                print("Intra in a doua")
                front_x_min, front_y_min, front_x_max, front_y_max = classes[0][0]
                print(f"Coordonate front: {classes[0][0]}")
                front_zone = []

                # Clasifică obiectele în funcție de poziție și reține box, label și score
                for box, label, score in zip(boxes, labels, scores):
                    x_min, y_min, x_max, y_max = box
                    print(f"Box {box} added to back_zone")
                    if front_x_min <= x_min <= front_x_max and front_x_min <= x_max <= front_x_max and front_y_min <= y_max <= front_y_max:
                        print(f"Box {box} added to back_zone")
                        front_zone.append((box, label, score))
                print(f"Front zone: {front_zone}")

                if front_zone:
                    # best_label = max(front_zone, key=lambda x: x[2])[1]
                    # front_label = max(front_zone, key=lambda x: x[2])[1]
                    front_box, front_label, front_score = max(front_zone, key=lambda x: x[2])
                    if front_score > car_parts["Windshield"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, front_box, front_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")

                        if front_label == 0:
                            car_parts["Windshield"] = {"status": 0, "message": "Windshield No Problem",
                                                       "confidence": front_score, "annotated_image": annotated_image}
                        elif front_label == 1:
                            car_parts["Windshield"] = {"status": 1, "message": "Windshield Problem",
                                                       "confidence": front_score, "annotated_image": annotated_image}
                        elif front_label == 2:
                            car_parts["Windshield"] = {"status": 2, "message": "No Windshield",
                                                       "confidence": front_score, "annotated_image": annotated_image}
                elif car_parts["Windshield"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[2][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")

                    car_parts["Windshield"] = {"status": -1, "message": "No Windshield", "confidence": 0,
                                               "annotated_image": annotated_image}

            elif 1 in detected_classes and 2 in detected_classes and 0 not in detected_classes:
                back_x_min, back_y_min, back_x_max, back_y_max = classes[2][0]
                front_mid_x = (back_x_min + back_x_max) / 2
                print(f"Coordonate back: {classes[2][0]}")
                back_zone = []
                # Clasifică obiectele în funcție de poziție
                if angleDirection == "Right":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if back_x_min <= x_max <= front_mid_x + front_mid_x / 4 and back_y_min <= y_max <= back_y_max:
                            print(f"Box {box} added to back_zone")
                            back_zone.append((box, label, score))
                elif angleDirection == "Left":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if front_mid_x - front_mid_x / 4 <= x_min <= back_x_max and back_y_min <= y_max <= back_y_max:
                            print(f"Box {box} added to back_zone")
                            back_zone.append((box, label, score))
                print(f"Dimenisune Back zone:{back_zone}")

                if back_zone:
                    # back_label = max(back_zone, key=lambda x: x[2])[1]
                    back_box, back_label, back_score = max(back_zone, key=lambda x: x[2])
                    if back_score > car_parts["RearWindow"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, back_box, back_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")

                        if back_label == 0:
                            car_parts["RearWindow"] = {"status": 0, "message": "Rear Window No Problem", "confidence": back_score, "annotated_image": annotated_image}
                        elif back_label == 1:
                            car_parts["RearWindow"] = {"status": 1, "message": "Rear Window Problem", "confidence": back_score, "annotated_image": annotated_image}
                        elif back_label == 2:
                            car_parts["RearWindow"] = {"status": 2, "message": "No Rear Window", "confidence": back_score, "annotated_image": annotated_image}
                elif car_parts["RearWindow"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[2][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")
                    car_parts["RearWindow"] = {"status": -1, "message": "No Rear Window","confidence": 0, "annotated_image": annotated_image}
            elif 1 in detected_classes and 2 not in detected_classes and 0 not in detected_classes:
                back_x_min, back_y_min, back_x_max, back_y_max = classes[1][0]
                print(f"Coordonate back: {classes[1][0]}")
                back_zone = []
                # Clasifică obiectele în funcție de poziție și reține box, label și score
                for box, label, score in zip(boxes, labels, scores):
                    x_min, y_min, x_max, y_max = box
                    if back_x_min-back_y_min/4 <= x_min <= back_x_max and back_x_min <= x_max <= back_x_max+back_x_max/4 and back_y_min <= y_max <= back_y_max:
                        print(f"Box {box} added to back_zone")
                        back_zone.append((box, label, score))
                print(f"Dimenisune Back zone:{back_zone}")
                if back_zone:
                    # back_label = max(back_zone, key=lambda x: x[2])[1]
                    back_box, back_label, back_score = max(back_zone, key=lambda x: x[2])
                    if back_score > car_parts["RearWindow"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, back_box, back_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")

                        if back_label == 0:
                            car_parts["RearWindow"] = {"status": 0, "message": "Rear Window No Problem",
                                                       "confidence": back_score, "annotated_image": annotated_image}
                        elif back_label == 1:
                            car_parts["RearWindow"] = {"status": 1, "message": "Rear Window Problem",
                                                       "confidence": back_score, "annotated_image": annotated_image}
                        elif back_label == 2:
                            car_parts["RearWindow"] = {"status": 2, "message": "No Rear Window", "confidence": back_score,
                                                       "annotated_image": annotated_image}
                elif car_parts["RearWindow"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[2][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")
                    car_parts["RearWindow"] = {"status": -1, "message": "No Rear Window", "confidence": 0,
                                               "annotated_image": annotated_image}


    def detect_hoodtrunk(self, image_path, angleDirection, classes,car_parts):
        # load image
        original_image = cv2.imread(image_path)
        # veify if the image work
        if original_image is None:
            raise ValueError(f"Error to load the image {image_path}")

        # load YOLO on the image
        # Modelul YOLO este apelat cu imaginea ca intrare.
        results = self.model(image_path)[0]

        # extract the directions
        # se foloseste .cpu(), pt ca tensorii lucreaza pe gpu, dar tu ai nevoie de cpu
        boxes = results.boxes.xyxy.cpu().numpy()
        # Acesta returnează coordonatele bounding box-urilor în format [x_min, y_min, x_max, y_max], unde:
        scores = results.boxes.conf.cpu().numpy()  # Conține scorul de încredere (probabilitatea) pentru fiecare detecție YOLO
        labels = results.boxes.cls.cpu().numpy()  # Conține indicele clasei fiecărui obiect detectat: 0:Front,1:Back, 2:Side

        print(f"Image: {os.path.basename(image_path)}")
        print(f"Classes detected: {labels}")

        # Checks detected class combinations(will make a vector with those labels)
        # detected_classes = set(labels)

        annotated_image1 = original_image.copy()
        detected_classes = set(classes.keys())
        print(f"Detected classes: {detected_classes}")
        print(f"Classes: {classes}")
        # determina daca sunt elemente
        if len(scores) > 0:

            # verifica daca este in side
            if 0 in detected_classes and 1 in detected_classes and 2 in detected_classes:

                print("Intra in prima")
                front_x_min, front_y_min, front_x_max, front_y_max = classes[0][0]
                print(f"Coordonate front: {classes[0][0]}")
                back_x_min, back_y_min, back_x_max, back_y_max = classes[1][0]
                print(f"Coordonate back: {classes[1][0]}")

                front_zone = []
                back_zone = []
                if angleDirection == "Right":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if front_x_min-front_x_min/4 <= x_min <= front_x_max and front_y_min <= y_max <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            front_zone.append((box, label, score))
                        elif back_x_min <= x_max <= back_x_max+back_x_max/4 and back_y_min <= y_max <= back_y_max:
                            print(f"Box {box} added to back_zone")
                            back_zone.append((box, label, score))
                elif angleDirection == "Left":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if back_x_min-back_x_min/4 <= x_min <= back_x_max and back_y_min <= y_max <= back_y_max:
                            print(f"Box {box} added to back_zone")
                            back_zone.append((box, label, score))
                        elif front_x_min <= x_max <= front_x_max+front_x_max/4 and front_y_min <= y_max <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            front_zone.append((box, label, score))

                print(f"Front zone: {front_zone}")
                print(f"Back zone: {back_zone}")
                if front_zone:
                    # front_label = max(front_zone, key=lambda x: x[2])[1]
                    front_box, front_label, front_score = max(front_zone, key=lambda x: x[2])
                    if front_score > car_parts["Hood"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, front_box, front_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")

                        if front_label == 0:
                            car_parts["Hood"] = {"status": 0, "message": "Hood No Problem","confidence": front_score, "annotated_image": annotated_image}
                        elif front_label == 2:
                            car_parts["Hood"] = {"status": 1, "message": "Hood Problem","confidence": front_score, "annotated_image": annotated_image}
                        elif front_label == 4:
                            car_parts["Hood"] = {"status": 2, "message": "No Hood","confidence": front_score, "annotated_image": annotated_image}
                elif car_parts["Hood"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")
                    car_parts["Hood"] = {"status": -1, "message": "No Hood","confidence": 0, "annotated_image": annotated_image}

                print(f"Dimensiune back_zone{back_zone}")

                if back_zone:
                    # back_label = max(back_zone, key=lambda x: x[2])[1]
                    back_box, back_label, back_score = max(back_zone, key=lambda x: x[2])
                    if back_score > car_parts["Trunk"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, back_box, back_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")

                        if back_label == 1:
                            car_parts["Trunk"] = {"status": 0, "message": "Trunk No Problem", "confidence": back_score, "annotated_image": annotated_image}
                        elif back_label == 3:
                            car_parts["Trunk"] = {"status": 1, "message": "Trunk Problem", "confidence": back_score, "annotated_image": annotated_image}
                        elif back_label == 5:
                            car_parts["Trunk"] = {"status": 2, "message": "No Trunk", "confidence": back_score, "annotated_image": annotated_image}
                elif car_parts["Trunk"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[1][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")

                    car_parts["Trunk"] = {"status": -1, "message": "No Trunk","confidence": 0, "annotated_image": annotated_image}


            elif (0 in detected_classes and 1 not in detected_classes and 2 in detected_classes) or (0 in detected_classes and 1 not in detected_classes and 2 not in detected_classes):
                print("Intra in a doua")
                front_x_min, front_y_min, front_x_max, front_y_max = classes[0][0]
                print(f"Coordonate front: {classes[0][0]}")
                front_zone = []

                if angleDirection == "Right":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        print(f"Box {box} added to back_zone")
                        if front_x_min-front_x_min/4 <= x_min <= front_x_max and front_y_min <= y_max <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            front_zone.append((box, label, score))
                elif angleDirection == "Left":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        print(f"Box {box} added to back_zone")
                        if front_x_min <= x_max <= front_x_max+front_x_max/4 and front_y_min <= y_max <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            front_zone.append((box, label, score))
                else:
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        print(f"Box {box} added to back_zone")
                        if front_x_min-front_x_min/4 <= x_min <= front_x_max and front_x_min <= x_max <= front_x_max+front_x_max/4 and front_y_min <= y_max <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            front_zone.append((box, label, score))
                print(f"Front zone: {front_zone}")

                if front_zone:
                    # front_label = max(front_zone, key=lambda x: x[2])[1]
                    front_box, front_label, front_score = max(front_zone, key=lambda x: x[2])
                    if front_score > car_parts["Hood"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, front_box, front_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")

                        if front_label == 0:
                            car_parts["Hood"] = {"status": 0, "message": "Hood No Problem", "confidence": front_score,
                                                 "annotated_image": annotated_image}
                        elif front_label == 2:
                            car_parts["Hood"] = {"status": 1, "message": "Hood Problem", "confidence": front_score,
                                                 "annotated_image": annotated_image}
                        elif front_label == 4:
                            car_parts["Hood"] = {"status": 2, "message": "No Hood", "confidence": front_score,
                                                 "annotated_image": annotated_image}
                elif car_parts["Hood"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")
                    car_parts["Hood"] = {"status": -1, "message": "No Hood", "confidence": 0,
                                         "annotated_image": annotated_image}

            elif (1 in detected_classes and 2 in detected_classes and 0 not in detected_classes) or (1 in detected_classes and 2 not in detected_classes and 0 not in detected_classes):
                back_x_min, back_y_min, back_x_max, back_y_max = classes[1][0]
                print(f"Coordonate back: {classes[1][0]}")
                back_zone = []
                # Clasifică obiectele în funcție de poziție
                if angleDirection == "Right":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if back_x_min <= x_max <= back_x_max+back_x_max/4 and back_y_min <= y_max <= back_y_max:
                            print(f"Box {box} added to back_zone")
                            back_zone.append((box, label, score))
                elif angleDirection == "Left":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if back_x_min-back_x_min/4 <= x_min <= back_x_max and back_y_min <= y_max <= back_y_max:
                            print(f"Box {box} added to back_zone")
                            back_zone.append((box, label, score))
                else:
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if back_x_min-back_x_min/4 <= x_min <= back_x_max and back_x_min <= x_max <= back_x_max + back_x_max / 4 and back_y_min <= y_max <= back_y_max:
                            print(f"Box {box} added to back_zone")
                            back_zone.append((box, label, score))
                print(f"Dimenisune Back zone:{back_zone}")
                if back_zone:
                    # back_label = max(back_zone, key=lambda x: x[2])[1]
                    back_box, back_label, back_score = max(back_zone, key=lambda x: x[2])
                    if back_score > car_parts["Trunk"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, back_box, back_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")

                        if back_label == 1:
                            car_parts["Trunk"] = {"status": 0, "message": "Trunk No Problem", "confidence": back_score,
                                                  "annotated_image": annotated_image}
                        elif back_label == 3:
                            car_parts["Trunk"] = {"status": 1, "message": "Trunk Problem", "confidence": back_score,
                                                  "annotated_image": annotated_image}
                        elif back_label == 5:
                            car_parts["Trunk"] = {"status": 2, "message": "No Trunk", "confidence": back_score,
                                                  "annotated_image": annotated_image}
                elif car_parts["Trunk"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[1][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")

                    car_parts["Trunk"] = {"status": -1, "message": "No Trunk", "confidence": 0,
                                          "annotated_image": annotated_image}


    def detect_taillight(self, image_path, angleDirection, classes,car_parts):
        # load image
        original_image = cv2.imread(image_path)
        # veify if the image work
        if original_image is None:
            raise ValueError(f"Error to load the image {image_path}")

        # load YOLO on the image
        # Modelul YOLO este apelat cu imaginea ca intrare.
        results = self.model(image_path)[0]

        # extract the directions
        # se foloseste .cpu(), pt ca tensorii lucreaza pe gpu, dar tu ai nevoie de cpu
        boxes = results.boxes.xyxy.cpu().numpy()
        # Acesta returnează coordonatele bounding box-urilor în format [x_min, y_min, x_max, y_max], unde:
        scores = results.boxes.conf.cpu().numpy()  # Conține scorul de încredere (probabilitatea) pentru fiecare detecție YOLO
        labels = results.boxes.cls.cpu().numpy()  # Conține indicele clasei fiecărui obiect detectat: 0:Front,1:Back, 2:Side

        print(f"Image: {os.path.basename(image_path)}")
        print(f"Classes detected: {labels}")

        # Checks detected class combinations(will make a vector with those labels)
        # detected_classes = set(labels)

        annotated_image1 = original_image.copy()

        detected_classes = set(classes.keys())
        print(f"Detected classes: {detected_classes}")
        print(f"Classes: {classes}")
        # determina daca sunt elemente
        if len(scores) > 0:

            # verifica daca este in side
            if 0 not in detected_classes and 1 in detected_classes and 2 not in detected_classes:

                print("Intra in prima")
                front_x_min, front_y_min, front_x_max, front_y_max = classes[1][0]
                print(f"Coordonate front: {classes[1][0]}")

                front_mid_x = (front_x_min + front_x_max) / 2  # Calculăm mijlocul zonei front

                right_zone = []
                left_zone = []

                # Clasifică obiectele în funcție de poziție și reține box, label și score
                for box, label, score in zip(boxes, labels, scores):
                    x_min, y_min, x_max, y_max = box

                    if front_y_min <= y_min <= front_y_max:
                        if x_min >= front_mid_x:  # Obiectul este în jumătatea stângă
                            print(f"Box {box} added to right_zone")
                            right_zone.append((box, label, score))
                        elif x_max <= front_mid_x:  # Obiectul este în jumătatea dreaptă
                            print(f"Box {box} added to left_zone")
                            left_zone.append((box, label, score))


                if right_zone:
                    #right_label = max(right_zone, key=lambda x: x[2])[1]
                    right_box, right_label, right_score = max(right_zone, key=lambda x: x[2])
                    if right_score > car_parts["RightTaillight"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, right_box, right_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")
                        if right_label == 0:
                            car_parts["RightTaillight"] = {"status": 0, "message": "Right Taillight No Problem",
                                                           "confidence": right_score, "annotated_image": annotated_image}
                        elif right_label == 1:
                            car_parts["RightTaillight"] = {"status": 1, "message": "Right Taillight Problem",
                                                           "confidence": right_score, "annotated_image": annotated_image}
                        elif right_label == 2:
                            car_parts["RightTaillight"] = {"status": 2, "message": "No Right Taillight",
                                                           "confidence": right_score, "annotated_image": annotated_image}
                elif car_parts["RightTaillight"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[1][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")
                    car_parts["RightTaillight"] = {"status": -1, "message": "No Right Taillight",
                                                       "confidence": 0, "annotated_image": annotated_image}


                if left_zone:
                    # left_label = max(left_zone, key=lambda x: x[2])[1]
                    left_box, left_label, left_score = max(left_zone, key=lambda x: x[2])
                    if left_score > car_parts["LeftTaillight"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, left_box, left_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")
                        if left_label == 0:
                            car_parts["LeftTaillight"] = {"status": 0, "message": "Left Taillight No Problem",
                                                           "confidence": left_score, "annotated_image": annotated_image}
                        elif left_label == 1:
                            car_parts["LeftTaillight"] = {"status": 1, "message": "Left Taillight Problem",
                                                           "confidence": left_score, "annotated_image": annotated_image}
                        elif left_label == 2:
                            car_parts["LeftTaillight"] = {"status": 2, "message": "No Left Taillight",
                                                           "confidence": left_score, "annotated_image": annotated_image}
                elif car_parts["LeftTaillight"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[1][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")
                    car_parts["LeftTaillight"] = {"status": -1, "message": "No Left Taillight",
                                                       "confidence": 0, "annotated_image": annotated_image}


            elif (0 not in detected_classes and 1 not in detected_classes and 2 in detected_classes) or (
                    0 not in detected_classes and 1 in detected_classes and 2 in detected_classes):
                print("Intra in a doua")
                front_x_min, front_y_min, front_x_max, front_y_max = classes[1][0]
                print(f"Coordonate front: {classes[1][0]}")

                if angleDirection == "Right":
                    right_zone = []
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if front_x_min <= x_min <= front_x_max and front_y_min <= y_min <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            right_zone.append((box, label, score))
                    if right_zone:
                        # right_label = max(right_zone, key=lambda x: x[2])[1]
                        right_box, right_label, right_score = max(right_zone, key=lambda x: x[2])
                        if right_score > car_parts["RightTaillight"].get("confidence", 0):
                            annotated_image = self.draw_detections(annotated_image1, right_box, right_label)
                            if annotated_image is None:
                                print("Eroare: Nu am reușit să adnotez imaginea!")
                            else:
                                print("Imaginea a fost adnotată corect.")
                            if right_label == 0:
                                car_parts["RightTaillight"] = {"status": 0, "message": "Right Taillight No Problem",
                                                               "confidence": right_score,
                                                               "annotated_image": annotated_image}
                            elif right_label == 1:
                                car_parts["RightTaillight"] = {"status": 1, "message": "Right Taillight Problem",
                                                               "confidence": right_score,
                                                               "annotated_image": annotated_image}
                            elif right_label == 2:
                                car_parts["RightTaillight"] = {"status": 2, "message": "No Right Taillight",
                                                               "confidence": right_score,
                                                               "annotated_image": annotated_image}
                    elif car_parts["RightTaillight"].get("confidence", -1) == -1:
                        annotated_image = self.draw_detections(annotated_image1, classes[1][0], 2)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                        else:
                            print("Imaginea a fost adnotată corect în caz de fallback.")
                        car_parts["RightTaillight"] = {"status": -1, "message": "No Right Taillight",
                                                       "confidence": 0, "annotated_image": annotated_image}

                elif angleDirection == "Left":
                    left_zone = []
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if front_x_min <= x_max <= front_x_max and front_y_min <= y_min <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            left_zone.append((box, label, score))
                    if left_zone:
                        # left_label = max(left_zone, key=lambda x: x[2])[1]
                        left_box, left_label, left_score = max(left_zone, key=lambda x: x[2])
                        if left_score > car_parts["LeftTaillight"].get("confidence", 0):
                            annotated_image = self.draw_detections(annotated_image1, left_box, left_label)
                            if annotated_image is None:
                                print("Eroare: Nu am reușit să adnotez imaginea!")
                            else:
                                print("Imaginea a fost adnotată corect.")
                            if left_label == 0:
                                car_parts["LeftTaillight"] = {"status": 0, "message": "Left Taillight No Problem",
                                                              "confidence": left_score,
                                                              "annotated_image": annotated_image}
                            elif left_label == 1:
                                car_parts["LeftTaillight"] = {"status": 1, "message": "Left Taillight Problem",
                                                              "confidence": left_score,
                                                              "annotated_image": annotated_image}
                            elif left_label == 2:
                                car_parts["LeftTaillight"] = {"status": 2, "message": "No Left Taillight",
                                                              "confidence": left_score,
                                                              "annotated_image": annotated_image}
                    elif car_parts["LeftTaillight"].get("confidence", -1) == -1:
                        annotated_image = self.draw_detections(annotated_image1, classes[1][0], 2)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                        else:
                            print("Imaginea a fost adnotată corect în caz de fallback.")
                        car_parts["LeftTaillight"] = {"status": -1, "message": "No Left Taillight",
                                                      "confidence": 0, "annotated_image": annotated_image}


    def detect_headlight(self, image_path, angleDirection, classes,car_parts):
        # load image
        original_image = cv2.imread(image_path)
        # veify if the image work
        if original_image is None:
            raise ValueError(f"Error to load the image {image_path}")

        # load YOLO on the image
        # Modelul YOLO este apelat cu imaginea ca intrare.
        results = self.model(image_path)[0]

        # extract the directions
        # se foloseste .cpu(), pt ca tensorii lucreaza pe gpu, dar tu ai nevoie de cpu
        boxes = results.boxes.xyxy.cpu().numpy()
        # Acesta returnează coordonatele bounding box-urilor în format [x_min, y_min, x_max, y_max], unde:
        scores = results.boxes.conf.cpu().numpy()  # Conține scorul de încredere (probabilitatea) pentru fiecare detecție YOLO
        labels = results.boxes.cls.cpu().numpy()  # Conține indicele clasei fiecărui obiect detectat: 0:Front,1:Back, 2:Side

        print(f"Image: {os.path.basename(image_path)}")
        print(f"Classes detected: {labels}")

        # Checks detected class combinations(will make a vector with those labels)
        # detected_classes = set(labels)
        annotated_image1 = original_image.copy()

        detected_classes = set(classes.keys())
        print(f"Detected classes: {detected_classes}")
        print(f"Classes: {classes}")
        # determina daca sunt elemente
        if len(scores) > 0:

            # verifica daca este in side
            if 0 in detected_classes and 1 not in detected_classes and 2 not in detected_classes:

                print("Intra in prima")
                front_x_min, front_y_min, front_x_max, front_y_max = classes[0][0]
                print(f"Coordonate front: {classes[0][0]}")

                front_mid_x = (front_x_min + front_x_max) / 2  # Calculăm mijlocul zonei front

                right_zone = []
                left_zone = []

                # Clasifică obiectele în funcție de poziție și reține box, label și score
                for box, label, score in zip(boxes, labels, scores):
                    x_min, y_min, x_max, y_max = box

                    if front_y_min <= y_min <= front_y_max:
                        if x_max <= front_mid_x:  # Obiectul este în jumătatea stângă
                            print(f"Box {box} added to right_zone")
                            right_zone.append((box, label, score))
                        elif x_min >= front_mid_x:  # Obiectul este în jumătatea dreaptă
                            print(f"Box {box} added to left_zone")
                            left_zone.append((box, label, score))


                if right_zone:
                    # right_label = max(right_zone, key=lambda x: x[2])[1]
                    right_box, right_label, right_score = max(right_zone, key=lambda x: x[2])
                    if right_score > car_parts["RightHeadlight"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, right_box, right_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")
                        if right_label == 0:
                            car_parts["RightHeadlight"] = {"status": 0, "message": "Right Headlight No Problem",
                                                           "confidence": right_score, "annotated_image": annotated_image}
                        elif right_label == 1:
                            car_parts["RightHeadlight"] = {"status": 1, "message": "Right Headlight Problem",
                                                           "confidence": right_score, "annotated_image": annotated_image}
                        elif right_label == 2:
                            car_parts["RightHeadlight"] = {"status": 2, "message": "No Right Headlight",
                                                           "confidence": right_score, "annotated_image": annotated_image}


                elif car_parts["RightHeadlight"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")
                    car_parts["RightHeadlight"] = {"status": -1, "message": "No Right Headlight", "confidence": 0,
                                                   "annotated_image": annotated_image}


                if left_zone:
                    # left_label = max(left_zone, key=lambda x: x[2])[1]
                    left_box, left_label, left_score = max(left_zone, key=lambda x: x[2])
                    if left_score > car_parts["LeftHeadlight"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, left_box, left_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")
                        if left_label == 0:
                            car_parts["LeftHeadlight"] = {"status": 0, "message": "Left Headlight No Problem",
                                                          "confidence": left_score, "annotated_image": annotated_image}
                        elif left_label == 1:
                            car_parts["LeftHeadlight"] = {"status": 1, "message": "Left Headlight Problem",
                                                          "confidence": left_score, "annotated_image": annotated_image}
                        elif left_label == 2:
                            car_parts["LeftHeadlight"] = {"status": 2, "message": "No Left Headlight",
                                                          "confidence": left_score, "annotated_image": annotated_image}
                        # Aplică draw_detections doar dacă există un left_label valid


                elif car_parts["LeftHeadlight"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")
                    car_parts["LeftHeadlight"] = {"status": -1, "message": "No Left Headlight", "confidence": 0,
                                                  "annotated_image": annotated_image}


            elif (0 in detected_classes and 1 in detected_classes and 2 in detected_classes) or (0 not in detected_classes and 1 not in detected_classes and 2 in detected_classes) or (
                    0 in detected_classes and 1 not in detected_classes and 2 in detected_classes):
                print("Intra in a doua")
                front_x_min, front_y_min, front_x_max, front_y_max = classes[0][0]
                print(f"Coordonate front: {classes[0][0]}")

                if angleDirection == "Right":
                    right_zone = []
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if front_x_min <= x_min <= front_x_max and front_y_min <= y_min <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            right_zone.append((box, label, score))
                    if right_zone:
                        # right_label = max(right_zone, key=lambda x: x[2])[1]
                        right_box, right_label, right_score = max(right_zone, key=lambda x: x[2])
                        if right_score > car_parts["RightHeadlight"].get("confidence", 0):
                            annotated_image = self.draw_detections(annotated_image1, right_box, right_label)
                            if annotated_image is None:
                                print("Eroare: Nu am reușit să adnotez imaginea!")
                            else:
                                print("Imaginea a fost adnotată corect.")
                            if right_label == 0:
                                car_parts["RightHeadlight"] = {"status": 0, "message": "Right Headlight No Problem",
                                                               "confidence": right_score,
                                                               "annotated_image": annotated_image}
                            elif right_label == 1:
                                car_parts["RightHeadlight"] = {"status": 1, "message": "Right Headlight Problem",
                                                               "confidence": right_score,
                                                               "annotated_image": annotated_image}
                            elif right_label == 2:
                                car_parts["RightHeadlight"] = {"status": 2, "message": "No Right Headlight",
                                                               "confidence": right_score,
                                                               "annotated_image": annotated_image}


                    elif car_parts["RightHeadlight"].get("confidence", -1) == -1:
                        annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                        else:
                            print("Imaginea a fost adnotată corect în caz de fallback.")
                        car_parts["RightHeadlight"] = {"status": -1, "message": "No Right Headlight", "confidence": 0,
                                                       "annotated_image": annotated_image}

                elif angleDirection == "Left":
                    print("Intra bine")
                    left_zone = []
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if front_x_min <= x_max <= front_x_max and front_y_min <= y_min <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            left_zone.append((box, label, score))

                    if left_zone:
                        # left_label = max(left_zone, key=lambda x: x[2])[1]
                        left_box, left_label, left_score = max(left_zone, key=lambda x: x[2])
                        if left_score > car_parts["LeftHeadlight"].get("confidence", 0):
                            annotated_image = self.draw_detections(annotated_image1, left_box, left_label)
                            if annotated_image is None:
                                print("Eroare: Nu am reușit să adnotez imaginea!")
                            else:
                                print("Imaginea a fost adnotată corect.")
                            if left_label == 0:
                                car_parts["LeftHeadlight"] = {"status": 0, "message": "Left Headlight No Problem",
                                                              "confidence": left_score,
                                                              "annotated_image": annotated_image}
                            elif left_label == 1:
                                car_parts["LeftHeadlight"] = {"status": 1, "message": "Left Headlight Problem",
                                                              "confidence": left_score,
                                                              "annotated_image": annotated_image}
                            elif left_label == 2:
                                car_parts["LeftHeadlight"] = {"status": 2, "message": "No Left Headlight",
                                                              "confidence": left_score,
                                                              "annotated_image": annotated_image}
                            # Aplică draw_detections doar dacă există un left_label valid


                    elif car_parts["LeftHeadlight"].get("confidence", -1) == -1:
                        annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                        else:
                            print("Imaginea a fost adnotată corect în caz de fallback.")
                        car_parts["LeftHeadlight"] = {"status": -1, "message": "No Left Headlight", "confidence": 0,
                                                      "annotated_image": annotated_image}



    def detect_bumper(self, image_path, angleDirection, classes, car_parts):
        # load image
        original_image = cv2.imread(image_path)
        if original_image is None:
            raise ValueError(f"Error loading the image {image_path}")

        # load YOLO on the image
        results = self.model(image_path)[0]

        # extract the bounding boxes, scores, and labels
        boxes = results.boxes.xyxy.cpu().numpy()
        scores = results.boxes.conf.cpu().numpy()
        labels = results.boxes.cls.cpu().numpy()
        print(f"Boxes car: {boxes}")
        print(f"Scores car: {scores}")
        print(f"Labels car: {labels}")
        print(f"Image: {os.path.basename(image_path)}")

        print(f"Image: {os.path.basename(image_path)}")
        print(f"Classes detected: {labels}")

        detected_classes = set(classes.keys())
        print(f"Detected classes: {detected_classes}")
        print(f"Classes: {classes}")

        #front_boxes = [box for label, box in zip(labels, boxes) if label == 0]
        front_boxes = [box for label, box in zip(labels, boxes)]
        print(f"{front_boxes}")
        back_boxes = [box for label, box in zip(labels, boxes) if label == 1]

        annotated_image1 = original_image.copy()
        detected_classes = set(classes.keys())
        print(f"Detected classes: {detected_classes}")
        print(f"Classes: {classes}")
        #determina daca sunt elemente
        if len(scores)>0:

            #verifica daca este in side
            if 0 in detected_classes and 1 in detected_classes and 2 in detected_classes:

                print("Intra in prima")
                front_x_min, front_y_min, front_x_max, front_y_max = classes[0][0]
                print(f"Coordonate front: {classes[0][0]}")
                back_x_min, back_y_min, back_x_max, back_y_max = classes[1][0]
                print(f"Coordonate back: {classes[1][0]}")


                front_zone = []
                back_zone = []
                if angleDirection == "Right":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if front_x_min <= x_min <= front_x_max and front_y_min <= y_min <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            front_zone.append((box, label, score))
                        elif back_x_min <= x_max <= back_x_max and back_y_min <= y_min <= back_y_max:
                            print(f"Box {box} added to back_zone")
                            back_zone.append((box, label, score))
                elif angleDirection == "Left":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if back_x_min <= x_min <= back_x_max and back_y_min <= y_min <= back_y_max:
                            print(f"Box {box} added to back_zone")
                            back_zone.append((box, label, score))
                        elif front_x_min <= x_max <= front_x_max and front_y_min <= y_min <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            front_zone.append((box, label, score))


                if front_zone:
                    #front_label = max(front_zone, key=lambda x: x[2])[1]
                    front_box, front_label, front_score = max(front_zone, key=lambda x: x[2])
                    if front_score > car_parts["FrontBumper"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, front_box, front_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")

                        if front_label == 0:
                            car_parts["FrontBumper"] = {"status": 0, "message": "Front Bumper No Problem", "confidence": front_score, "annotated_image": annotated_image}
                        elif front_label == 2:
                            car_parts["FrontBumper"] = {"status": 1, "message": "Front Bumper Problem","confidence": front_score, "annotated_image": annotated_image}
                        elif front_label == 4:
                            car_parts["FrontBumper"] = {"status": 2, "message": "No Front Bumper","confidence": front_score, "annotated_image": annotated_image}
                elif car_parts["FrontBumper"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")

                    car_parts["FrontBumper"] = {"status": -1, "message": "No Front Bumper", "confidence": 0, "annotated_image": annotated_image}


                print(f"Dimensiune back_zone{back_zone}")
                if back_zone:
                    #back_label = max(back_zone, key=lambda x: x[2])[1]
                    back_box, back_label, back_score = max(back_zone, key=lambda x: x[2])
                    if back_score > car_parts["RearBumper"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, back_box, back_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")
                        if back_label == 1:
                            car_parts["RearBumper"] = {"status": 0, "message": "Rear Bumper No Problem", "confidence": back_score, "annotated_image": annotated_image}
                        elif back_label == 3:
                            car_parts["RearBumper"] = {"status": 1, "message": "Rear Bumper Problem", "confidence": back_score, "annotated_image": annotated_image}
                        elif back_label == 5:
                            car_parts["RearBumper"] = {"status": 2, "message": "No Rear Bumper", "confidence": back_score, "annotated_image": annotated_image}
                elif car_parts["RearBumper"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")
                    car_parts["RearBumper"] = {"status": -1, "message": "No Rear Bumper", "confidence": 0, "annotated_image": annotated_image}


            elif (0 in detected_classes and 1 not in detected_classes and 2 not in detected_classes) or (0 in detected_classes and 1 not in detected_classes and 2 in detected_classes):
                print("Intra in a doua")
                front_x_min, front_y_min, front_x_max, front_y_max = classes[0][0]
                print(f"Coordonate front: {classes[0][0]}")
                front_zone = []

                if angleDirection == "Right":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if front_x_min-front_x_min/4 <= x_min <= front_x_max and front_y_min <= y_min <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            front_zone.append((box, label, score))
                elif angleDirection == "Left":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if front_x_min <= x_max <= front_x_max+front_x_max/4 and front_y_min <= y_min <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            front_zone.append((box, label, score))
                else:
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if front_x_min <= x_max <= front_x_max+front_x_max/4 and front_x_min-front_x_min/4 <= x_min <= front_x_max and front_y_min <= y_min <= front_y_max:
                            print(f"Box {box} added to back_zone")
                            front_zone.append((box, label, score))

                print(f"Elem front zone: {front_zone}")
                if front_zone:
                    # front_label = max(front_zone, key=lambda x: x[2])[1]
                    front_box, front_label, front_score = max(front_zone, key=lambda x: x[2])
                    if front_score > car_parts["FrontBumper"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, front_box, front_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")

                        if front_label == 0:
                            car_parts["FrontBumper"] = {"status": 0, "message": "Front Bumper No Problem",
                                                        "confidence": front_score, "annotated_image": annotated_image}
                        elif front_label == 2:
                            car_parts["FrontBumper"] = {"status": 1, "message": "Front Bumper Problem",
                                                        "confidence": front_score, "annotated_image": annotated_image}
                        elif front_label == 4:
                            car_parts["FrontBumper"] = {"status": 2, "message": "No Front Bumper",
                                                        "confidence": front_score, "annotated_image": annotated_image}
                elif car_parts["FrontBumper"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[0][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")

                    car_parts["FrontBumper"] = {"status": -1, "message": "No Front Bumper", "confidence": 0,
                                                "annotated_image": annotated_image}
            elif (1 in detected_classes and 0 not in detected_classes and 2 not in detected_classes) or (1 in detected_classes and 2 in detected_classes and 0 not in detected_classes):
                back_x_min, back_y_min, back_x_max, back_y_max = classes[1][0]
                print(f"Coordonate back: {classes[1][0]}")
                back_zone = []
                # Clasifică obiectele în funcție de poziție
                if angleDirection == "Right":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if back_x_min <= x_max <= back_x_max+back_x_max/4 and back_y_min <= y_min <= back_y_max:
                            print(f"Box {box} added to back_zone")
                            back_zone.append((box, label, score))
                elif angleDirection == "Left":
                    # Clasifică obiectele în funcție de poziție și reține box, label și score
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if back_x_min-back_y_min/4 <= x_min <= back_x_max and back_y_min <= y_min <= back_y_max:
                            print(f"Box {box} added to back_zone")
                            back_zone.append((box, label, score))
                else:
                    for box, label, score in zip(boxes, labels, scores):
                        x_min, y_min, x_max, y_max = box
                        if back_x_min <= x_max <= back_x_max+back_x_max/4 and back_x_min-back_y_min/4 <= x_min <= back_x_max and back_y_min <= y_min <= back_y_max:
                            print(f"Box {box} added to back_zone")
                            back_zone.append((box, label, score))
                print(f"Dimenisune Back zone:{back_zone}")

                print(f"Dimensiune back_zone{back_zone}")
                if back_zone:
                    # back_label = max(back_zone, key=lambda x: x[2])[1]
                    back_box, back_label, back_score = max(back_zone, key=lambda x: x[2])
                    if back_score > car_parts["RearBumper"].get("confidence", 0):
                        annotated_image = self.draw_detections(annotated_image1, back_box, back_label)
                        if annotated_image is None:
                            print("Eroare: Nu am reușit să adnotez imaginea!")
                        else:
                            print("Imaginea a fost adnotată corect.")
                        if back_label == 1:
                            car_parts["RearBumper"] = {"status": 0, "message": "Rear Bumper No Problem",
                                                       "confidence": back_score, "annotated_image": annotated_image}
                        elif back_label == 3:
                            car_parts["RearBumper"] = {"status": 1, "message": "Rear Bumper Problem",
                                                       "confidence": back_score, "annotated_image": annotated_image}
                        elif back_label == 5:
                            car_parts["RearBumper"] = {"status": 2, "message": "No Rear Bumper",
                                                       "confidence": back_score, "annotated_image": annotated_image}
                elif car_parts["RearBumper"].get("confidence", -1) == -1:
                    annotated_image = self.draw_detections(annotated_image1, classes[1][0], 2)
                    if annotated_image is None:
                        print("Eroare: Nu am reușit să adnotez imaginea în caz de fallback!")
                    else:
                        print("Imaginea a fost adnotată corect în caz de fallback.")
                    car_parts["RearBumper"] = {"status": -1, "message": "No Rear Bumper", "confidence": 0,
                                               "annotated_image": annotated_image}



    def detect_backwing(self, image_path, angleDirection, classes,car_parts):
        # Load image
        original_image = cv2.imread(image_path)
        if original_image is None:
            raise ValueError(f"Error loading the image {image_path}")

        # Run YOLO model on the image
        results = self.model(image_path)[0]

        # Extract bounding boxes, scores, and labels
        boxes = results.boxes.xyxy.cpu().numpy()
        scores = results.boxes.conf.cpu().numpy()
        labels = results.boxes.cls.cpu().numpy()

        print(f"Image: {os.path.basename(image_path)}")
        print(f"Classes detected: {labels}")

        # Adapt classes to new detect_labels return format
        detected_classes = set(classes.keys())  # Extragem doar clasele detectate
        annotated_image1 = original_image.copy()

        if len(scores) > 0:
            max_score_index = np.argmax(scores)  # Selectăm elementul cu cel mai mare scor
            best_label = labels[max_score_index]
            best_box = boxes[max_score_index]  # Coordonatele elementului best_label
            best_score = scores[max_score_index]
            best_x_min, best_y_min, best_x_max, best_y_max = best_box

            is_right_of_side = False
            is_left_of_side = False
            valid_right_position, valid_left_position = False, False  # Verifică dacă detecția este validă pe baza coordonatelor

            # Verificăm dacă avem un element "Side" (label 2)
            if 2 in classes and isinstance(classes[2], list) and len(classes[2]) > 0:
                side_box = classes[2][0]  # Ia primul box
                side_x_min, side_y_min, side_x_max, side_y_max = side_box

                side_mid_x = (side_x_min + side_x_max) / 2
                add_some_size = (side_x_min + side_x_max) / 4
                # Verificăm dacă best_label este în dreapta față de Side
                is_left_of_side = best_x_min >= side_mid_x - add_some_size
                is_right_of_side = best_x_max <= side_mid_x + add_some_size
                print(f"{side_mid_x}")

                # Verificăm dacă elementul este în zona corectă față de Side
                valid_left_position = (
                        best_x_min < side_x_max and ((best_y_min <= side_y_max and best_y_min >= side_y_min) and
                                                     (best_y_max <= side_y_max and best_y_max >= side_y_min))
                )
                valid_right_position = (
                        best_x_max > side_x_min and ((best_y_min <= side_y_max and best_y_min >= side_y_min) and
                                                     (best_y_max <= side_y_max and best_y_max >= side_y_min))
                )
                print(
                    f"{best_x_min, best_y_min, best_x_max, best_y_max} si \n {side_x_min, side_y_min, side_x_max, side_y_max}")

            if angleDirection == "Right":
                if valid_right_position:  # Doar dacă poziția este validă, actualizăm car_parts
                    if best_score > car_parts["RearRightWing"].get("confidence", 0):
                        if (0 in detected_classes and 1 in detected_classes and 2 in detected_classes) or (0 in detected_classes and 2 in detected_classes) or (
                                1 in detected_classes and 2 in detected_classes):

                            if is_right_of_side:
                                annotated_image = self.draw_detections(annotated_image1, best_box, best_label)
                                if annotated_image is None:
                                    print("Eroare: Nu am reușit să adnotez imaginea!")
                                else:
                                    print("Imaginea a fost adnotată corect.")
                                if best_label == 0:
                                    car_parts["RearRightWing"] = {"status": 0, "message": "Back Right Wing No Problem", "confidence": best_score,"annotated_image":annotated_image}
                                elif best_label == 1:
                                    car_parts["RearRightWing"] = {"status": 1, "message": "Back Right Wing Problem", "confidence": best_score,"annotated_image":annotated_image}
                                elif best_label == 2:
                                    car_parts["RearRightWing"] = {"status": 2, "message": "No Back Right Wing", "confidence": best_score,"annotated_image":annotated_image}

                            else:
                                side_box = classes[2][0]  # Luăm primul box pentru Side
                                annotated_image = self.draw_detections(annotated_image1, side_box,
                                                                       2)  # Folosim label 2 pentru Side
                                if annotated_image is not None:
                                    print("Imaginea a fost adnotată cu side_box.")
                                    car_parts["FrontRightWing"]["annotated_image"] = annotated_image
                                else:
                                    print("Eroare: Nu am reușit să adnotez imaginea cu side_box!")
                                car_parts["RearRightWing"] = {"status": -1, "message": "No Back Right Wing", "confidence": 0, "annotated_image": annotated_image}

            elif angleDirection == "Left":
                if valid_left_position:
                    if best_score > car_parts["RearLeftWing"].get("confidence", 0):
                        if (0 in detected_classes and 1 in detected_classes and 2 in detected_classes) or (0 in detected_classes and 2 in detected_classes) or (
                                1 in detected_classes and 2 in detected_classes):
                            if is_left_of_side:
                                annotated_image = self.draw_detections(annotated_image1, best_box, best_label)
                                if annotated_image is None:
                                    print("Eroare: Nu am reușit să adnotez imaginea!")
                                else:
                                    print("Imaginea a fost adnotată corect.")
                                if best_label == 0:
                                    car_parts["RearLeftWing"] = {"status": 0, "message": "Back Left Wing No Problem", "confidence": best_score, "annotated_image": annotated_image}
                                elif best_label == 1:
                                    car_parts["RearLeftWing"] = {"status": 1, "message": "Back Left Wing Problem", "confidence": best_score, "annotated_image": annotated_image}
                                elif best_label == 2:
                                    car_parts["RearLeftWing"] = {"status": 2, "message": "No Back Left Wing", "confidence": best_score, "annotated_image": annotated_image}

                            else:
                                side_box = classes[2][0]  # Luăm primul box pentru Side
                                annotated_image = self.draw_detections(annotated_image1, side_box,2)  # Folosim label 2 pentru Side
                                if annotated_image is not None:
                                    print("Imaginea a fost adnotată cu side_box.")
                                    car_parts["FrontRightWing"]["annotated_image"] = annotated_image
                                else:
                                    print("Eroare: Nu am reușit să adnotez imaginea cu side_box!")
                                car_parts["RearLeftWing"] = {"status": -1, "message": "No Back Left Wing", "confidence": 0, "annotated_image": annotated_image}
                                print("There is the problem")



    def detect_frontwing(self, image_path, angleDirection, classes,car_parts):
        # Load image
        original_image = cv2.imread(image_path)
        if original_image is None:
            raise ValueError(f"Error loading the image {image_path}")

        # Run YOLO model on the image
        results = self.model(image_path)[0]

        # Extract bounding boxes, scores, and labels
        boxes = results.boxes.xyxy.cpu().numpy()
        scores = results.boxes.conf.cpu().numpy()
        labels = results.boxes.cls.cpu().numpy()

        print(f"Labels car: {labels}")
        print(f"Scores car: {scores}")

        print(f"Image: {os.path.basename(image_path)}")
        print(f"Classes detected: {labels}")

        # Adapt classes to new detect_labels return format
        detected_classes = set(classes.keys())  # Extragem doar clasele detectate

        if len(scores) > 0:
            max_score_index = np.argmax(scores)  # Selectăm elementul cu cel mai mare scor
            best_label = labels[max_score_index]
            best_box = boxes[max_score_index]  # Coordonatele elementului best_label
            best_score = scores[max_score_index]
            best_x_min, best_y_min, best_x_max, best_y_max = best_box

            is_right_of_side = False
            is_left_of_side = False
            valid_right_position,valid_left_position = False,False  # Verifică dacă detecția este validă pe baza coordonatelor

            # Verificăm dacă avem un element "Side" (label 2)
            if 2 in classes and isinstance(classes[2], list) and len(classes[2]) > 0:
                side_box = classes[2][0]  # Ia primul box
                side_x_min, side_y_min, side_x_max, side_y_max = side_box

                side_mid_x = (side_x_min + side_x_max) / 2
                add_some_size = (side_x_min + side_x_max) / 4
                # Verificăm dacă best_label este în dreapta față de Side
                is_right_of_side = best_x_min >= side_mid_x-add_some_size
                is_left_of_side = best_x_max <= side_mid_x+add_some_size
                print(f"{side_mid_x}")

                # Verificăm dacă elementul este în zona corectă față de Side
                valid_right_position = (
                        best_x_min<side_x_max and ((best_y_min <= side_y_max and best_y_min >= side_y_min) and
                        (best_y_max <= side_y_max and best_y_max >= side_y_min))
                )
                valid_left_position = (
                        best_x_max > side_x_min and ((best_y_min <= side_y_max and best_y_min >= side_y_min) and
                                                     (best_y_max <= side_y_max and best_y_max >= side_y_min))
                )
                print(f"{best_x_min, best_y_min, best_x_max, best_y_max} si \n {side_x_min, side_y_min, side_x_max, side_y_max}")
            annotated_image1 = original_image.copy()
            if angleDirection == "Right":
                if valid_right_position:  # Doar dacă poziția este validă, actualizăm car_parts
                    if best_score > car_parts["FrontRightWing"].get("confidence", 0):
                        if (0 in detected_classes and 1 in detected_classes and 2 in detected_classes) or (0 in detected_classes and 2 in detected_classes) or (
                                1 in detected_classes and 2 in detected_classes):

                            if is_right_of_side:
                                annotated_image = self.draw_detections(annotated_image1, best_box, best_label)
                                if annotated_image is None:
                                    print("Eroare: Nu am reușit să adnotez imaginea!")
                                else:
                                    print("Imaginea a fost adnotată corect.")
                                if best_label == 0:
                                    car_parts["FrontRightWing"] = {"status": 0, "message": "Front Right Wing No Problem", "confidence": best_score,"annotated_image":annotated_image}
                                elif best_label == 1:
                                    car_parts["FrontRightWing"] = {"status": 1, "message": "Front Right Wing Problem", "confidence": best_score,"annotated_image":annotated_image}
                                elif best_label == 2:
                                    car_parts["FrontRightWing"] = {"status": 2, "message": "No Front Right Wing", "confidence": best_score,"annotated_image":annotated_image}

                            else:
                                side_box = classes[2][0]  # Luăm primul box pentru Side
                                annotated_image = self.draw_detections(annotated_image1, side_box,
                                                                       2)  # Folosim label 2 pentru Side
                                if annotated_image is not None:
                                    print("Imaginea a fost adnotată cu side_box.")
                                    car_parts["FrontRightWing"]["annotated_image"] = annotated_image
                                else:
                                    print("Eroare: Nu am reușit să adnotez imaginea cu side_box!")
                                car_parts["FrontRightWing"] = {"status": -1, "message": "Front No Right Wing", "confidence": 0, "annotated_image": annotated_image}

            elif angleDirection == "Left":
                if valid_left_position:
                    if best_score > car_parts["FrontLeftWing"].get("confidence", 0):
                        if (0 in detected_classes and 1 in detected_classes and 2 in detected_classes) or (0 in detected_classes and 2 in detected_classes) or (
                                1 in detected_classes and 2 in detected_classes):
                            if is_left_of_side:
                                annotated_image = self.draw_detections(annotated_image1, best_box, best_label)
                                if annotated_image is None:
                                    print("Eroare: Nu am reușit să adnotez imaginea!")
                                else:
                                    print("Imaginea a fost adnotată corect.")
                                if best_label == 0:
                                    car_parts["FrontLeftWing"] = {"status": 0, "message": "Front Left Wing No Problem", "confidence": best_score, "annotated_image": annotated_image}
                                elif best_label == 1:
                                    car_parts["FrontLeftWing"] = {"status": 1, "message": "Front Left Wing Problem", "confidence": best_score, "annotated_image": annotated_image}
                                elif best_label == 2:
                                    car_parts["FrontLeftWing"] = {"status": 2, "message": "No Front Left Wing", "confidence": best_score, "annotated_image": annotated_image}

                            else:
                                side_box = classes[2][0]  # Luăm primul box pentru Side
                                annotated_image = self.draw_detections(annotated_image1, side_box,2)  # Folosim label 2 pentru Side
                                if annotated_image is not None:
                                    print("Imaginea a fost adnotată cu side_box.")
                                    car_parts["FrontLeftWing"]["annotated_image"] = annotated_image
                                else:
                                    print("Eroare: Nu am reușit să adnotez imaginea cu side_box!")
                                car_parts["FrontLeftWing"] = {"status": -1, "message": "No Front Left Wing", "confidence": 0, "annotated_image": annotated_image}
                                print("There is the problem")