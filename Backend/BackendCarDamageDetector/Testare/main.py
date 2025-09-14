from ultralytics import YOLO

# model = YOLO("yolov8n.pt")
model = YOLO("yolov8l.pt")

results = model.train(data="config.yaml", epochs=15, device="cpu")  # train the model