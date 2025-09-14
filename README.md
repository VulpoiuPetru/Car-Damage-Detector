# CarDamage Detector

## Overview

CarDamage Detector is an innovative mobile application designed to automatically identify and evaluate visible car damages based on user-provided images. Built as part of a bachelor's thesis in Computer Science at Transilvania University of Brașov, this project integrates advanced artificial intelligence techniques, particularly computer vision, to assist drivers in real-world scenarios such as minor accidents, vehicle inspections, or second-hand car purchases. The app detects damages like scratches, dents, cracks, deformed parts, or missing components on the car's body, generates detailed reports, estimates repair costs, and recommends nearby auto services or parts suppliers.

Inspired by a personal experience in a minor traffic accident, where accurately documenting damages and finding repair options was challenging, the application aims to simplify these processes for non-experts. It provides quick, accessible diagnostics without requiring technical knowledge, reducing time, stress, and costs associated with vehicle assessments.

Unlike existing solutions like Tractable (B2B-focused for insurers), Click-Ins (for leasing companies), ProovStation (hardware-dependent and expensive), or CarVertical (history reports without real-time visual detection), CarDamage Detector is user-centric and accessible to individuals. It features distinct roles for regular users (damage detection and reports) and partners (auto services uploading offers via CSV files), creating an ecosystem that connects demand with supply. Key innovations include real-time visual damage detection, structured reports on affected car elements (e.g., front bumper, hood, right headlight), comprehensive cost estimates (parts + labor), and integration with local partner offers.

The system is divided into a backend for processing and a frontend mobile app built with .NET MAUI for cross-platform compatibility (iOS/Android). It leverages YOLOv8 for object detection, trained on annotated datasets, and supports features like user authentication, CSV uploads for partner offers, and damage visualization.

## Features

- **Automatic Damage Detection**: Upload or capture photos of the vehicle; the app uses AI models to detect and classify damages on car elements (e.g., scratches, dents, broken parts).
- **Detailed Reports**: Generates structured reports listing affected components, damage types, estimated repair costs (based on partner data), and labor requirements.
- **Cost Estimation**: Integrates partner-uploaded CSV data to provide real-time estimates for parts and services.
- **Partner Integration**: Auto services or parts suppliers can register as partners and upload standardized CSV files with offers (part codes, prices, labor costs).
- **User Roles**:
  - **Regular Users**: Detect damages, view reports, and get service recommendations.
  - **Partners**: Upload and manage CSV offers, view uploaded files, delete files, and list available CSVs.
- **Authentication**: Secure login and signup pages for users and partners.
- **Frontend Interfaces**: Start screen, login/signup, partner dashboard (for CSV management), and detection page (for image uploads and results).
- **Backend APIs**: RESTful endpoints for damage detection, CSV processing, entity ID management, and data visualization.
- **Database Integration**: Stores user data, partner offers, and detection results in SQL Server.
- **Model Training**: Custom YOLOv8 models for car direction detection (e.g., front, side, rear) and element/damage identification, trained on annotated images via CVAT.ai.

## Technologies and Frameworks

### Technologies
- **Python**: Core language for backend logic and AI processing.
- **OpenCV (cv2)**: For image processing and manipulation.
- **Google Colab**: Used for model training and development in a cloud environment.
- **CVAT.ai**: Annotation tool for creating labeled datasets for YOLOv8 training.
- **Google Cloud Platform**: Hosts servers and databases for scalable deployment.
- **SSMS + SQL Server**: Database management for storing user, partner, and offer data.
- **REST API + Uvicorn**: Fast asynchronous server for handling API requests.
- **Docker**: Containerization for consistent deployment across environments.

### Frameworks
- **.NET MAUI**: Cross-platform framework for building the mobile frontend (iOS/Android).
- **TensorFlow + Ultralytics YOLOv8**: For object detection models; YOLOv8 is trained for car elements and damages.
- **FastAPI**: Backend framework for creating efficient, auto-documented APIs.

## Backend Structure

The backend is powered by FastAPI and runs the main server in `ElementDetector.py`, which orchestrates damage detection by calling supporting scripts:
- **CarElements.py**: Handles detection of specific car components (e.g., bumper, hood).
- **AngleCar.py**: Determines the car's viewing angle/direction (front, side, rear) using a dedicated YOLOv8 model.
- **ClasaUnghiMasina.py**: Class for car angle classification, aiding in accurate element mapping.

Key classes:
- **CarDirectionDetector**: Detects the vehicle's orientation to contextualize damages.
- **CarElementsDetector**: Identifies and classifies damages on detected elements.

APIs include:
- Getting/inserting entity IDs.
- Uploading and processing CSV files (for partner offers).
- Viewing CSV data.
- Deleting CSV files.
- Listing uploaded CSVs.
- Core damage detection endpoint: Processes images, runs models, and returns reports with costs.

Pre-trained models are included in the backend for car direction and element detection. Custom training datasets were annotated using CVAT.ai and trained on Google Colab.

## Setup Instructions

### Prerequisites
- Python 3.12+ with libraries: OpenCV, Ultralytics (YOLOv8), FastAPI, Uvicorn.
- SQL Server instance (local or cloud).
- Google Cloud account for deployment.
- Docker for containerization.

### Configuration
1. **Email Setup for Developer Notifications**:
   - Create a developer email account to send data (e.g., reports).
   - In `ElementDetector.py` (backend), set:

```python
EMAIL_ADDRESS = "your_developer_email@example.com
"
EMAIL_PASSWORD = "your_password"
```


2. **Database Connection**:
- In `conn_str` from `ElementDetector.py`:


```python
conn_str = (
"DRIVER={ODBC Driver 17 for SQL Server};"
"SERVER=your_desktop_name;"
"DATABASE=your_database_name;"
"Trusted_Connection=yes;"
)
```

- Replace `your_desktop_name` and `your_database_name` with your SQL Server details.

3. **Running the Backend**:
- Install dependencies: `pip install fastapi uvicorn opencv-python ultralytics pyodbc`.
- Run the server: `uvicorn ElementDetector:app --reload`.

4. **Frontend Setup**:
- Use Visual Studio with .NET MAUI workload.
- Build and deploy for iOS/Android.

### Model Training
To customize elements or damages, create a training dataset:
- Annotate images using CVAT.ai (for bounding boxes and labels).
- Train on Google Colab:

```python
from google.colab import drive
drive.mount('/content/drive')
!pip install ultralytics
from ultralytics import YOLO

model = YOLO("yolov8l.pt")  # Or "yolov8n.pt" for a smaller model

config_path = "/content/drive/MyDrive/Licenta/ExDetectMasina/config.yaml"

results = model.train(data=config_path, epochs=150, device="cuda")  # Use "cpu" if no GPU
```

- Update backend models with the new weights.

### Deployment
- For global access: Set up a server and database on Google Cloud Platform.
- Dockerize the backend: Create a Dockerfile and deploy to a container service.

## Database Schema
The SQL Server database includes tables for:
- Users and partners (authentication).
- CSV offers (part codes, prices, labor).
- Detection results (damages, elements, costs).

## Future Developments
- Enhanced accuracy with larger datasets and fine-tuning.
- Integration with maps for real-time service recommendations.
- Support for video inputs or 3D reconstructions.
- Multi-language support and expanded damage types.
- Cloud-based model updates for partners.

This project demonstrates the practical application of AI in automotive diagnostics, making vehicle assessments more efficient and user-friendly. Contributions and feedback are welcome! For more details, refer to the thesis document.
