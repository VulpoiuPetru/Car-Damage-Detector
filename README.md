# CarDamage Detector
 
CarDamage Detector is a cross-platform mobile application that automatically identifies and evaluates visible car damage from user-provided photos. Built as a bachelor's thesis project (Computer Science, Transilvania University of Brașov), it combines a custom-trained YOLOv8 computer vision pipeline with a FastAPI backend and a .NET MAUI mobile app.
 
## Motivation
 
The idea came from a real minor traffic accident: documenting the damage accurately for the *constatare amiabilă* (friendly accident report) was harder than it should have been, and afterwards, finding a nearby service and getting a real cost estimate took more time, calls, and guesswork than expected. CarDamage Detector automates that first step — point your phone at the car, and get a structured breakdown of what's damaged, what it's likely to cost, and which nearby partners can fix it.
 
## Screenshots
 
**Detect a damaged vehicle** — select or capture photos, optionally add car details for a more accurate cost estimate:
 
<img width="452" height="843" alt="screenshot-detect-input" src="https://github.com/user-attachments/assets/c697719f-c540-4cd4-8680-a312b000ae38" />

 
**AI-generated damage annotations** — the trained YOLOv8 models localize and label each affected component:
 
<img width="402" height="798" alt="screenshot-damage-annotation" src="https://github.com/user-attachments/assets/d10285c4-7dbf-44e8-abcc-6c0e3cc71b14" />

 
## Overview
 
The app detects damages like scratches, dents, cracks, deformed parts, or missing components on the car's body, generates detailed reports, estimates repair costs, and recommends nearby auto services or parts suppliers.
 
Unlike existing solutions like Tractable (B2B-focused for insurers), Click-Ins (for leasing companies), ProovStation (hardware-dependent and expensive), or CarVertical (history reports without real-time visual detection), CarDamage Detector is user-centric and accessible to individuals. It features distinct roles for regular users (damage detection and reports) and partners (auto services uploading offers via CSV files), creating an ecosystem that connects demand with supply.
 
The system is divided into a backend for processing and a frontend mobile app built with .NET MAUI for cross-platform compatibility (iOS/Android). It leverages YOLOv8 for object detection, trained on annotated datasets, and supports features like user authentication, CSV uploads for partner offers, and damage visualization.
 
## Features
 
- **Automatic damage detection** — upload or capture photos of the vehicle; the app uses AI models to detect and classify damage on car elements (e.g. scratches, dents, broken parts).
- **Detailed reports** — structured reports listing affected components, damage types, estimated repair costs (based on partner data), and labor requirements.
- **Cost estimation** — integrates partner-uploaded CSV data to provide real-time estimates for parts and services.
- **Partner integration** — auto services or parts suppliers register as partners and upload standardized CSV files with offers (part codes, prices, labor costs).
- **User roles**:
  - *Regular users*: detect damage, view reports, get service recommendations.
  - *Partners*: upload and manage CSV offers, view uploaded files, delete files, list available CSVs.
- **Authentication** — login and signup for both users and partners.
- **Model training pipeline** — custom YOLOv8 models for car direction detection (front/side/rear) and element/damage identification, trained on images annotated via CVAT.ai.
## Technologies and frameworks
 
| Layer | Technologies |
|---|---|
| AI / CV | Python, OpenCV, TensorFlow, Ultralytics YOLOv8, CVAT.ai (annotation), Google Colab (training) |
| Backend | FastAPI, Uvicorn, SQL Server (SSMS) |
| Frontend | .NET MAUI (iOS/Android), C# |
| Infra | Docker, Google Cloud Platform |
 
## Backend structure
 
The backend runs on FastAPI, with the main server in `ElementDetector.py`, which orchestrates damage detection by calling supporting modules:
 
- `CarElements.py` — detection of specific car components (bumper, hood, etc.)
- `AngleCar.py` / `ClasaUnghiMasina.py` — determines the car's viewing angle (front, side, rear) with a dedicated YOLOv8 model, used to map damage to the right component
Key classes: `CarDirectionDetector` (vehicle orientation) and `CarElementsDetector` (damage identification and classification).
 
APIs cover: entity ID lookup/insertion, CSV upload/view/delete/list (partner offers), and the core `/detect` endpoint — processes images, runs the models, and returns a structured report with cost estimates.
 
## Setup
 
### Prerequisites
 
- Python 3.12+ (OpenCV, Ultralytics, FastAPI, Uvicorn)
- SQL Server instance (local or cloud)
- Docker, for containerized deployment
- Visual Studio with the .NET MAUI workload, for the mobile app
### Configuration
 
The backend reads its email and database credentials from environment variables — copy `.env.example` to `.env` and fill in real values rather than editing `ElementDetector.py` directly:
 
```
EMAIL_ADDRESS=your_developer_email@example.com
EMAIL_PASSWORD=your_app_password
DB_DRIVER={ODBC Driver 17 for SQL Server}
DB_SERVER=your_server_name
DB_DATABASE=your_database_name
```
 
### Running the backend
 
```bash
pip install fastapi uvicorn opencv-python ultralytics pyodbc python-dotenv
uvicorn ElementDetector:app --reload
```
 
### Running the frontend
 
Open the `.NET MAUI` project in Visual Studio and build/deploy for iOS or Android.
 
### Model training
 
To retrain or extend the detection models:
 
1. Annotate images in [CVAT.ai](https://www.cvat.ai/) (bounding boxes per component/damage class).
2. Train on Google Colab:
```python
from google.colab import drive
drive.mount('/content/drive')
!pip install ultralytics
from ultralytics import YOLO
 
model = YOLO("yolov8l.pt")
config_path = "/content/drive/MyDrive/Licenta/ExDetectMasina/config.yaml"
results = model.train(data=config_path, epochs=150, device="cuda")
```
 
3. Swap the resulting weights into the backend's model paths.
## Database schema
 
SQL Server tables for: users/partners (auth), CSV offers (part codes, prices, labor), and detection results (damages, elements, costs).
 
## Future developments
 
- Interior damage detection (dashboard, seats, airbags), not just exterior.
- Finer-grained damage severity classification (superficial vs. deep scratches, dent depth).
- Persistent login.
- Analysis history per user/vehicle.
- Partner rating/feedback loop.
---
 
This project was developed as a bachelor's thesis; the full written thesis (with architecture diagrams, model training details, and evaluation) is available on request.
