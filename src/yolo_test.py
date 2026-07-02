import os
import logging
from ultralytics import YOLO

# Suppress verbose deep learning tracking logs to keep the terminal clean
logging.getLogger("ultralytics").setLevel(logging.WARNING)

def verify_yolo_environment():
    print("=== [STEP 1] Initializing YOLO Environment ===")
    
    # Define where the weights should live (root folder)
    weights_filename = "yolov8n.pt"
    
    print(f"Loading {weights_filename}... If it's missing, Ultralytics will auto-download it.")
    
    try:
        # This single line instantiates the neural net and auto-downloads the weights
        model = YOLO(weights_filename)
        print("✅ Success: YOLOv8 Nano model weights successfully loaded into memory!")
        
        # Print out the generic labels it knows to prove the model is fully readable
        num_classes = len(model.names)
        print(f"ℹ️ The pre-trained model is capable of identifying {num_classes} distinct object classes.")
        print(f"👉 Class index 0 is mapped to: '{model.names[0]}'")
        print(f"👉 Class index 39 is mapped to: '{model.names[39]}'") # Usually a bottle
        
    except Exception as e:
        print(f"❌ Error during model initialization: {str(e)}")

if __name__ == "__main__":
    verify_yolo_environment()
    