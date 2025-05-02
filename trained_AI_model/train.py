from ultralytics import YOLO

# Loading the base model
model = YOLO("trained_AI_model\FoodLink.pt")

# Training using a custom training set consisting of multiple sets from Roboflow to increase the degree of accuracy
# model.train(data="AI_model_training\custom_data_set\data.yaml", epochs=10, imgsz=640)

# The model is trained so that the following class labels can be detected:
# ['apple', 'banana', 'orange', 'bell pepper', 'potato']



 
