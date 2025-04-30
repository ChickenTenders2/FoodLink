from ultralytics import YOLO

# Loading the base model
model = YOLO("YOLOv8s.pt")

# Training using several datasets to increase the degree of accuracy
model.train(data="model_training/training_data_1/data.yaml", epochs=50, imgsz=640)
model.train(data="model_training/training_data_2/data.yaml", epochs=50, imgsz=640)





