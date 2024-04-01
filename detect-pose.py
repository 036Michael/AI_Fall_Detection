from ultralytics import YOLO

model = YOLO('yolov8n-pose.pt')  # load an official model

# Train the model
results = model.predict(source=0 ,conf =0.8 ,show=True)  # predict on video stream