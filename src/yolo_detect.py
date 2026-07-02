import os
import glob
import logging
import pandas as pd
from ultralytics import YOLO

# Suppress deep learning debug lines to keep terminal clean
logging.getLogger("ultralytics").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

PHOTOS_DIR = "data/photos"
OUTPUT_CSV = "data/raw/yolo_detections.csv"

def classify_image_content(detected_classes):
    """
    Business Rules Engine: Categorizes an image based on the combination 
    of objects detected within its frame.
    """
    # Define what YOLO classes count as a physical product container
    product_indicators = {'bottle', 'cup', 'vase', 'bowl'}
    
    has_person = 'person' in detected_classes
    has_product = any(item in product_indicators for item in detected_classes)
    
    if has_person and has_product:
        return "promotional"
    elif has_product and not has_person:
        return "product_display"
    elif has_person and not has_product:
        return "lifestyle"
    else:
        return "other"

def run_object_detection_and_classification():
    logging.info("Starting Milestone 3 Business Classification Engine...")
    
    if not os.path.exists("yolov8n.pt"):
        logging.error("yolov8n.pt weights missing from root! Run Milestone 1.")
        return
        
    model = YOLO("yolov8n.pt")
    
    # Scan all image directories
    search_path = os.path.join(PHOTOS_DIR, "**", "*.jpg")
    image_files = glob.glob(search_path, recursive=True)
    
    if not image_files:
        logging.warning(f"No images discovered inside {PHOTOS_DIR}.")
        return
        
    logging.info(f"Discovered {len(image_files)} total images for classification processing.")
    
    classified_records = []
    
    for img_path in image_files:
        filename = os.path.basename(img_path)
        
        # Parse names: e.g., "CheMed123_97.jpg"
        name_part, _ = os.path.splitext(filename)
        try:
            if "_" in name_part:
                parts = name_part.split("_")
                channel_name = "_".join(parts[:-1])
                message_id = int(parts[-1])
            else:
                continue
        except Exception as e:
            logging.error(f"Failed parsing identifiers from filename {filename}: {str(e)}")
            continue
            
        # Run image through YOLO neural net
        outputs = model(img_path, conf=0.25)
        boxes = outputs[0].boxes
        
        # Gather ALL classes detected inside this specific single frame
        classes_in_image = []
        highest_confidence = 0.0
        primary_class = "none"
        
        for box in boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]
            conf = float(box.conf[0])
            
            classes_in_image.append(cls_name)
            # Track the strongest object detection score for our database reference
            if conf > highest_confidence:
                highest_confidence = conf
                primary_class = cls_name
                
        # Trigger our business rule mapping logic
        image_category = classify_image_content(classes_in_image)
        
        logging.info(f"Image {filename} evaluated as category: [{image_category.upper()}] (Found: {list(set(classes_in_image))})")
        
        # Store a single consolidated row per image asset
        classified_records.append({
            "message_id": message_id,
            "channel_name": channel_name,
            "detected_class": primary_class if len(boxes) > 0 else "none",
            "confidence_score": round(highest_confidence, 4),
            "image_category": image_category,
            "image_path": img_path
        })
        
    # Write to data lake CSV file
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df = pd.DataFrame(classified_records)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    
    logging.info(f"Classification successfully completed! Unified dataset written to: {OUTPUT_CSV}")

if __name__ == "__main__":
    run_object_detection_and_classification()
    