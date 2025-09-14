import base64
import csv
import random
import smtplib
import time

from ultralytics import YOLO
import os
import cv2
import asyncio
import aiofiles
from typing import List
import re

import json
import sys
from fastapi import FastAPI, UploadFile, File
import numpy as np
from ClasaUnghiMasina import CarDirectionDetector
from fastapi.middleware.cors import CORSMiddleware

import pyodbc

from fastapi import Form, HTTPException
import bcrypt
from datetime import datetime

from pydantic import PositiveInt

from email.message import EmailMessage

from CarElements import CarElementsDetector

from fastapi import Response


from typing import Optional



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)






BASE_DIR = os.path.dirname(os.path.abspath(__file__))


model_filenames = [
    "bestCar.pt",
    "bestAngleCar.pt",
    "bestFrontWing.pt",
    "bestBackWing.pt",
    "bestFrontBackBumper.pt",
    "bestHeadLight.pt",
    "bestDoor.pt",
    "bestMirror.pt",
    "bestPillarsRoof.pt",
    "bestTailLight.pt",
    "bestTrunkHood.pt",
    "bestWheel.pt",
    "bestWindow.pt",
    "bestWindshieldRearWindow.pt"
]


model_paths = [os.path.join(BASE_DIR, "TrainedSets", name) for name in model_filenames]


for path in model_paths:
    if not os.path.exists(path):
        print(f"NU a fost găsit: {path}")
    else:
        print(f"Găsit: {path}")




def initialize_car_parts():
    return {
        "FrontBumper": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "FrontRightWing": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "FrontLeftWing": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "RightHeadlight": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "LeftHeadlight": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "Hood": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "Windshield": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "RearBumper": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "RearRightWing": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "RearLeftWing": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "RightTaillight": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "LeftTaillight": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "Trunk": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "RearWindow": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "RightMirror": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "LeftMirror": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "FrontRightDoor": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "RearRightDoor": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "FrontLeftDoor": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "RearLeftDoor": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "FrontRightWindow": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "RearRightWindow": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "FrontLeftWindow": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "RearLeftWindow": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "FrontRightWheel": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "RearRightWheel": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "FrontLeftWheel": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "RearLeftWheel": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None},
        "PillarsRoof": {"status": 0, "message": "Unknown", "confidence": -1, "annotated_image": None}
    }

element_states = [0] * len(model_paths)


detectorCar = CarElementsDetector(model_paths[0])
detectorAngle = CarDirectionDetector(model_paths[1])
detectorFrontWing = CarElementsDetector(model_paths[2])
detectorBackWing = CarElementsDetector(model_paths[3])
detectorFrontBackBumper = CarElementsDetector(model_paths[4])
detectorHeadLight = CarElementsDetector(model_paths[5])
detectorDoor = CarElementsDetector(model_paths[6])
detectorMirror = CarElementsDetector(model_paths[7])
detectorPillarsRoof = CarElementsDetector(model_paths[8])
detectorTailLight = CarElementsDetector(model_paths[9])
detectorTrunkHood = CarElementsDetector(model_paths[10])
detectorWheel = CarElementsDetector(model_paths[11])
detectorWindow = CarElementsDetector(model_paths[12])
detectorWindshieldRearWindow = CarElementsDetector(model_paths[13])




conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=your_desktop_name"
    "DATABASE=your_database_name"
    "Trusted_Connection=yes;"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))




@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    cursor.execute("SELECT PasswordHash, Role FROM Users WHERE Username = ?", (username,))
    row = cursor.fetchone()
    if not row or not verify_password(password, row[0]):
        raise HTTPException(status_code=401, detail="Username sau parolă greșită")

    return {
        "message": "Autentificare reușită",
        "username": username,
        "role": row[1]
    }

@app.post("/signupUser/")
def signupUser(username: str = Form(...), password: str = Form(...), role: str = Form(...)):
    if role != "User":
        return Response(content="Invalid Role", status_code=400, media_type="text/plain")

    cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        return Response(content="Username already exists", status_code=400, media_type="text/plain")


    hashed_password = hash_password(password)

    cursor.execute(
        "INSERT INTO Users (Username, PasswordHash, Role) VALUES (?, ?, ?)",
        (username, hashed_password, role)
    )
    conn.commit()

    return {"message": f"Contul {username} a fost creat cu succes!", "role": role}
@app.post("/signupPartner/")
def signupPartner(username: str = Form(...), password: str = Form(...), role: str = Form(...),company_name: str = Form(...) ,company_number: str = Form(...),
                  company_email: str = Form(...),company_location: str = Form(...)):

    if role != "Partner":

        return Response(content="Invalid role", status_code=400, media_type="text/plain")

    cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        return Response(content="Username already exists", status_code=400, media_type="text/plain")

    hashed_password = hash_password(password)

    cursor.execute(
        "INSERT INTO Users (Username, PasswordHash, Role) OUTPUT INSERTED.UserId VALUES (?, ?, ?)",
        (username, hashed_password, role)
    )
    user_id = cursor.fetchone()[0]

    print("User ID obținut:", user_id)

    cursor.execute(
        "INSERT INTO Service (Name, Number, Email, Location, UserId) VALUES (?, ?, ?, ?, ?)",
        (company_name, company_number, company_email, company_location, user_id)
    )
    conn.commit()

    return {"message": f"Contul {username} a fost creat cu succes!", "role": role}


EMAIL_ADDRESS = "your email"
EMAIL_PASSWORD = "your password"


rate_limit = {}

MAX_CODES = 5
TIME_WINDOW = 600


@app.post("/send-code/")
async def send_code(email: str = Form(...)):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return Response(content="Invalid mail format", status_code=400, media_type="text/plain")

    now = time.time()
    timestamps = rate_limit.get(email, [])
    timestamps = [t for t in timestamps if now - t < TIME_WINDOW]

    if len(timestamps) >= MAX_CODES:
        return Response(content="Too many codes sent. Try again later.", status_code=429, media_type="text/plain")

    timestamps.append(now)
    rate_limit[email] = timestamps

    try:
        code = str(random.randint(100000, 999999))

        msg = EmailMessage()
        msg["Subject"] = "Verification Code"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email
        msg.set_content(f"Your verification code is: {code}")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        return {"success": True, "code": code}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_car_model_id(manufacturer: str, model: str, year: int):
    cursor.execute(
        "SELECT CarModelId FROM CarModels WHERE Manufacturer = ? AND Name = ? AND Year = ?",
        (manufacturer, model, year)
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(
        "INSERT INTO CarModels (Manufacturer, Name, Year) VALUES (?, ?, ?)",
        (manufacturer, model, year)
    )
    conn.commit()
    cursor.execute("SELECT @@IDENTITY")
    return cursor.fetchone()[0]

def get_component_id(code: str, name: str):
    cursor.execute("SELECT ComponentId FROM Components WHERE Code = ? AND Name = ?", (code,name))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(
        "INSERT INTO Components (Code, Name) VALUES (?, ?)",
        (code, name)
    )
    conn.commit()
    cursor.execute("SELECT @@IDENTITY")
    return cursor.fetchone()[0]

def get_service_id_by_user(user_id: int):
    cursor.execute("SELECT ServiceId FROM Service WHERE UserId = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    raise ValueError("The service associated with the user was not found.")


@app.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...), username: str = Form(...)):
    # Verificăm rolul utilizatorului și obținem UserId
    cursor.execute("SELECT UserId, Role FROM Users WHERE Username = ?", (username,))
    row = cursor.fetchone()
    if not row:
        return Response(content="User does not exist", status_code=401, media_type="text/plain")
    if row[1] != "Partner":
        return Response(content="Only partners can upload CSV files", status_code=403, media_type="text/plain")

    user_id = row[0]

    upload_dir = "./uploaded_files"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        with open(file_path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            expected_headers = {
                "Manufacturer", "CarModel", "Year", "ComponentCode", "Component",
                "Price", "LaborCost"
            }
            if not expected_headers.issubset(set(csv_reader.fieldnames)):
                return Response(content="CSV is missing required columns", status_code=400, media_type="text/plain")

            service_id = get_service_id_by_user(user_id)

            data_to_insert = []
            for row in csv_reader:
                car_model_id = get_car_model_id(row["Manufacturer"], row["CarModel"], int(row["Year"]))
                component_id = get_component_id(row["ComponentCode"], row["Component"])
                price = float(row["Price"])
                labor_cost = float(row["LaborCost"])
                data_to_insert.append((car_model_id, component_id, price, labor_cost))

        cursor.execute(
            "INSERT INTO UploadedFiles (UserId, Filename) VALUES (?, ?)",
            (user_id, filename)
        )
        conn.commit()
        cursor.execute("SELECT @@IDENTITY")
        file_id = cursor.fetchone()[0]

        for car_model_id, component_id, price, labor_cost in data_to_insert:
            cursor.execute(
                """
                INSERT INTO ComponentPrices (CarModelId, ComponentId, ServiceId, Price, LaborCost, FileId)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (car_model_id, component_id, service_id, price, labor_cost, file_id)
            )
        conn.commit()

    except Exception as e:
        conn.rollback()
        try:
            cursor.execute("DELETE FROM UploadedFiles WHERE Filename = ?", (filename,))
            conn.commit()
        except:
            pass
        if os.path.exists(file_path):
            os.remove(file_path)

        return Response(content=f"CSV processing error: {str(e)}", status_code=400, media_type="text/plain")
    return Response(content="The file was successfully processed and data has been inserted.", media_type="text/plain")


@app.get("/get_csv_data/")
async def get_csv_data(file_id: int, username: str):
    cursor.execute("""
        SELECT u.UserId FROM Users u
        JOIN UploadedFiles f ON u.UserId = f.UserId
        WHERE f.FileId = ? AND u.Username = ?
    """, (file_id, username))
    row = cursor.fetchone()
    if not row:
        return Response(content="Access denied or file not found", status_code=403, media_type="text/plain")

    cursor.execute("""
        SELECT cm.Manufacturer, cm.Name AS CarModel, cm.Year,
               c.Code AS ComponentCode, c.Name AS Component,
               cp.Price, cp.LaborCost
        FROM ComponentPrices cp
        JOIN CarModels cm ON cp.CarModelId = cm.CarModelId
        JOIN Components c ON cp.ComponentId = c.ComponentId
        WHERE cp.FileId = ?
    """, (file_id,))

    rows = cursor.fetchall()
    header = ["Manufacturer", "CarModel", "Year", "ComponentCode", "Component", "Price", "LaborCost"]
    data = [list(row) for row in rows]

    return {
        "columns": header,
        "rows": data
    }



@app.post("/delete_csv/")
async def delete_csv(file_id: PositiveInt = Form(...), username: str = Form(...)):
    cursor.execute("SELECT UserId, Role FROM Users WHERE Username = ?", (username,))
    row = cursor.fetchone()
    if not row:
        return Response(content="The user doesn't exist", status_code=401,media_type="text/plain")
    if row[1] != "Partner":
        return Response(content="Only partners can delete CSV files", status_code=403, media_type="text/plain")

    user_id = row[0]

    cursor.execute("SELECT Filename FROM UploadedFiles WHERE FileId = ? AND UserId = ?", (file_id, user_id))
    row = cursor.fetchone()
    if not row:
        return Response(content="File does not exist or does not belong to this user", status_code=404, media_type="text/plain")

    filename = row[0]
    file_path = os.path.join("./uploaded_files", filename)

    try:
        cursor.execute("SELECT CarModelId, ComponentId, ServiceId FROM ComponentPrices WHERE FileId = ?", (file_id,))
        associated_ids = cursor.fetchall()

        cursor.execute("DELETE FROM ComponentPrices WHERE FileId = ?", (file_id,))

        for car_model_id, component_id, service_id in associated_ids:
            cursor.execute("SELECT COUNT(*) FROM ComponentPrices WHERE CarModelId = ?", (car_model_id,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("DELETE FROM CarModels WHERE CarModelId = ?", (car_model_id,))

            cursor.execute("SELECT COUNT(*) FROM ComponentPrices WHERE ComponentId = ?", (component_id,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("DELETE FROM Components WHERE ComponentId = ?", (component_id,))

        cursor.execute("DELETE FROM UploadedFiles WHERE FileId = ?", (file_id,))
        conn.commit()

        # Ștergem fișierul fizic
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"The file {file_path} was not found on disk, but the database records were deleted.")
    except Exception as e:
        conn.rollback()
        return Response(content=f"Deletion error: {str(e)}", status_code=500, media_type="text/plain")
    return Response(content="File and all associated data were successfully deleted.", media_type="text/plain")



@app.get("/list_csvs/")
async def list_csvs(username: str):
    cursor.execute("SELECT UserId, Role FROM Users WHERE Username = ?", (username,))
    row = cursor.fetchone()
    if not row or row[1] != "Partner":
        return Response(content="Only partners can view CSVs", status_code=403, media_type="text/plain")
    user_id = row[0]

    cursor.execute(
        "SELECT FileId, Filename, UploadDate FROM UploadedFiles WHERE UserId = ?",
        (user_id,)
    )
    files = [{"file_id": row[0], "filename": row[1], "upload_date": row[2]} for row in cursor.fetchall()]
    return {"files": files}




def convert_floats(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.float32) or isinstance(obj, np.float64):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats(i) for i in obj]
    return obj


async def resize_and_compress(image_path, max_size=(800, 800), quality=80):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Invalid image file")

    h, w = image.shape[:2]
    scale = min(max_size[0] / w, max_size[1] / h)
    new_size = (int(w * scale), int(h * scale))
    resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

    compressed_path = f"compressed_{image_path}.jpg"
    cv2.imwrite(compressed_path, resized_image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return compressed_path


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def map_car_part_to_component_name(part: str) -> str:
    mapping = {
        "FrontBumper": "Front Bumper",
        "RearBumper": "Rear Bumper",
        "FrontRightWing": "Front Right Wing",
        "FrontLeftWing": "Front Left Wing",
        "RearRightWing": "Rear Right Wing",
        "RearLeftWing": "Rear Left Wing",
        "RightHeadlight": "Right Headlight",
        "LeftHeadlight": "Left Headlight",
        "RightTaillight": "Right Taillight",
        "LeftTaillight": "Left Taillight",
        "Hood": "Hood",
        "Trunk": "Trunk",
        "Windshield": "Windshield",
        "RearWindow": "Rear Window",
        "RightMirror": "Right Mirror",
        "LeftMirror": "Left Mirror",
        "FrontRightDoor": "Front Right Door",
        "RearRightDoor": "Rear Right Door",
        "FrontLeftDoor": "Front Left Door",
        "RearLeftDoor": "Rear Left Door",
        "FrontRightWindow": "Front Right Window",
        "RearRightWindow": "Rear Right Window",
        "FrontLeftWindow": "Front Left Window",
        "RearLeftWindow": "Rear Left Window",
        "FrontRightWheel": "Front Right Wheel",
        "RearRightWheel": "Rear Right Wheel",
        "FrontLeftWheel": "Front Left Wheel",
        "RearLeftWheel": "Rear Left Wheel",
        "PillarsRoof": "Pillars Roof"
    }
    return mapping.get(part, None)


@app.post("/detect/")
async def detect(images: List[UploadFile] = File(...), username: str = Form(...), manufacturer: str = Form(None), car_model: str = Form(None), year: str = Form(None)):
    cursor.execute("SELECT role FROM Users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if not row:
        return Response(content="Non-existent user", status_code=401, media_type="text/plain")

    if row[0] != "User":
        return Response(content="Only users can detect", status_code=403, media_type="text/plain")

    year_int = None
    if manufacturer and car_model and year:
        try:
            year_int = int(year.strip())
            manufacturer = manufacturer.strip()
            car_model = car_model.strip()
            print(f"Received car details: manufacturer={manufacturer}, car_model={car_model}, year={year_int}")
        except ValueError:
            return Response(content="The year must be a valid number!", status_code=400, media_type="text/plain")

    try:
        car_parts = initialize_car_parts()
        annotated_images = {}
        processed_any_image = False

        detectors = [
            detectorFrontWing.detect_frontwing,
            detectorBackWing.detect_backwing,
            detectorFrontBackBumper.detect_bumper,
            detectorHeadLight.detect_headlight,
            detectorTailLight.detect_taillight,
            detectorTrunkHood.detect_hoodtrunk,
            detectorWindshieldRearWindow.detect_windshieldrearwindow,
            detectorMirror.detect_mirror,
            detectorDoor.detect_door,
            detectorWindow.detect_window,
            detectorWheel.detect_wheel,
            detectorPillarsRoof.detect_pillarsroof,
        ]

        for idx, image in enumerate(images):
            image_path = f"temp_{image.filename}"

            async with aiofiles.open(image_path, "wb") as f:
                await f.write(await image.read())

            compressed_path = await resize_and_compress(image_path)
            os.remove(image_path)

            if not detectorCar.detect_car(compressed_path):
                encoded_original = encode_image_to_base64(compressed_path)
                annotated_images[f"original_{idx}"] = f"data:image/jpeg;base64,{encoded_original}"
                os.remove(compressed_path)
                continue

            processed_any_image = True
            encoded_original = encode_image_to_base64(compressed_path)
            annotated_images[f"original_{idx}"] = f"data:image/jpeg;base64,{encoded_original}"

            directionCar = detectorAngle.detect_direction(compressed_path)
            classesCar = detectorAngle.detect_labels(compressed_path)

            for detector in detectors:
                detector(compressed_path, directionCar, classesCar, car_parts)
                await asyncio.sleep(0.5)

            os.remove(compressed_path)

        if not processed_any_image:
            return Response(
                content=json.dumps(convert_floats({
                    "message": "No image contains exactly one car!",
                    "detected_parts": {},
                    "messages": {},
                    "annotated_images": annotated_images,
                    "service_info": {}
                })),
                status_code=200,
                media_type="application/json"
            )

        for part, details in car_parts.items():
            if ("annotated_image" in details and details["annotated_image"] is not None and
                    "status" in details and details["status"] in [1, 2]):
                annotated_image = details["annotated_image"]
                annotated_part_path = f"temp_annotated_{part}.jpg"
                cv2.imwrite(annotated_part_path, annotated_image)
                encoded_part_image = encode_image_to_base64(annotated_part_path)
                annotated_images[f"{part}_annotated"] = f"data:image/jpeg;base64,{encoded_part_image}"
                os.remove(annotated_part_path)

        # Filtrăm doar părțile cu status 1 sau 2
        detected_parts = {
            k: {key: val for key, val in v.items() if key != "annotated_image"}
            for k, v in car_parts.items()
            if isinstance(v.get("status"), (int, float)) and v.get("status") in [1, 2]
        }
        messages = {k: v.get("message", "No message") for k, v in detected_parts.items()}

        service_info = {}
        if manufacturer and car_model and year_int:
            print(f"Processing with car details for detected parts: {list(detected_parts.keys())}")

            cursor.execute(
                """
                SELECT CarModelId FROM CarModels
                WHERE Name = ? AND Manufacturer = ? AND Year = ?
                """,
                (car_model, manufacturer, year_int)
            )
            car_model_row = cursor.fetchone()
            if not car_model_row:
                print(f"No car model found for Manufacturer='{manufacturer}', CarModel='{car_model}', Year={year_int}")
                cursor.execute(
                    """
                    SELECT s.Name, s.Number, s.Email, s.Location
                    FROM Service s
                    """
                )
                rows = cursor.fetchall()
                for part in detected_parts.keys():
                    service_info[part] = [
                        {
                            "ServiceName": row[0],
                            "Number": row[1],
                            "Email": row[2],
                            "ServiceLocation": row[3]
                        }
                        for row in rows
                    ]
                return Response(
                    content=json.dumps(convert_floats({
                        "message": "Car model not found, displaying available services.",
                        "detected_parts": detected_parts,
                        "messages": messages,
                        "annotated_images": annotated_images,
                        "service_info": service_info
                    })),
                    status_code=200,
                    media_type="application/json"
                )
            car_model_id = car_model_row[0]
            print(
                f"Found CarModelId={car_model_id} for Manufacturer='{manufacturer}', CarModel='{car_model}', Year={year_int}")

            cursor.execute(
                """
                SELECT DISTINCT ComponentId FROM ComponentPrices
                WHERE CarModelId = ?
                """,
                (car_model_id,)
            )
            component_ids = [row[0] for row in cursor.fetchall()]
            print(f"Available ComponentIds for CarModelId={car_model_id}: {component_ids}")

            component_mapping = {}
            if component_ids:
                placeholders = ",".join("?" for _ in component_ids)
                cursor.execute(
                    f"""
                    SELECT ComponentId, Name FROM Components
                    WHERE ComponentId IN ({placeholders})
                    """,
                    component_ids
                )
                for row in cursor.fetchall():
                    component_mapping[row[0]] = row[1]
            print(f"Component mapping: {component_mapping}")

            reverse_mapping = {}
            for part in detected_parts.keys():
                component_name = map_car_part_to_component_name(part)
                if component_name:
                    # Inițializăm o listă pentru ComponentId-uri
                    reverse_mapping[part] = []
                    for component_id, name in component_mapping.items():
                        if name == component_name:
                            reverse_mapping[part].append(component_id)
            print(f"Reverse mapping (detected parts to ComponentIds): {reverse_mapping}")

            cursor.execute(
                """
                SELECT s.Name, s.Number, s.Email, s.Location, s.ServiceId
                FROM Service s
                """
            )
            all_services = [
                {
                    "ServiceName": row[0],
                    "Number": row[1],
                    "Email": row[2],
                    "ServiceLocation": row[3],
                    "ServiceId": row[4]
                }
                for row in cursor.fetchall()
            ]
            print(f"All available services: {[s['ServiceName'] for s in all_services]}")

            for part in detected_parts.keys():
                service_info[part] = []
                if part in reverse_mapping:
                    component_ids_for_part = reverse_mapping[part]
                    print(f"Found ComponentIds={component_ids_for_part} for part={part}")

                    for component_id in component_ids_for_part:
                        cursor.execute(
                            """
                            SELECT cp.Price, cp.LaborCost, s.Name, s.Number, s.Email, s.Location, c.Name, c.Code
                            FROM ComponentPrices cp
                            JOIN CarModels cm ON cm.CarModelId = cp.CarModelId
                            JOIN Components c ON c.ComponentId = cp.ComponentId
                            JOIN Service s ON s.ServiceId = cp.ServiceId
                            WHERE cm.CarModelId = ? AND c.ComponentId = ?
                            """,
                            (car_model_id, component_id)
                        )
                        rows = cursor.fetchall()
                        if rows:
                            print(
                                f"Found {len(rows)} price entries for CarModelId={car_model_id}, ComponentId={component_id}")
                            service_info[part].extend([
                                {
                                    "ServiceName": row[2],
                                    "Number": row[3],
                                    "Email": row[4],
                                    "ServiceLocation": row[5],
                                    "Price": float(row[0]),
                                    "LaborCost": float(row[1]),
                                    "ComponentName": row[6],
                                    "ComponentCode": row[7]
                                }
                                for row in rows
                            ])
                        else:
                            print(
                                f"No component prices found for CarModelId={car_model_id}, ComponentId={component_id}")

                for service in all_services:
                    if not any(s["ServiceName"] == service["ServiceName"] for s in service_info[part]):
                        service_info[part].append({
                            "ServiceName": service["ServiceName"],
                            "Number": service["Number"],
                            "Email": service["Email"],
                            "ServiceLocation": service["ServiceLocation"],
                            "Price": 0.0,
                            "LaborCost": 0.0,
                            "ComponentName": "",
                            "ComponentCode": ""
                        })
                print(f"service_info[{part}]: {service_info[part]}")

        else:
            cursor.execute(
                """
                SELECT s.Name, s.Number, s.Email, s.Location
                FROM Service s
                """
            )
            rows = cursor.fetchall()
            for part in detected_parts.keys():
                service_info[part] = [
                    {
                        "ServiceName": row[0],
                        "Number": row[1],
                        "Email": row[2],
                        "ServiceLocation": row[3]
                    }
                    for row in rows
                ]

        return Response(
            content=json.dumps(convert_floats({
                "message": "Valid images were successfully processed!",
                "detected_parts": detected_parts,
                "messages": messages,
                "annotated_images": annotated_images,
                "service_info": service_info
            })),
            status_code=200,
            media_type="application/json"
        )

    except Exception as e:
        print(f"Error type: {type(e)}: {e}")
        return Response(content=f"An error occurred: {str(e)}", status_code=500, media_type="text/plain")

#Open server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)



