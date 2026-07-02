import os
import logging
import psycopg2
import pandas as pd
from psycopg2 import extras
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

CSV_PATH = "data/raw/yolo_detections.csv"

def load_yolo_csv_to_postgres():
    if not os.path.exists(CSV_PATH):
        logging.error(f"Missing source file: {CSV_PATH}. Run Milestone 3 first!")
        return

    df = pd.read_csv(CSV_PATH)
    records = list(df.itertuples(index=False, name=None))

    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()
        
        # Build structure inside our raw landing schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw.yolo_detections (
                message_id INT,
                channel_name VARCHAR(255),
                detected_class VARCHAR(100),
                confidence_score NUMERIC,
                image_category VARCHAR(100),
                image_path TEXT,
                inserted_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        
        cursor.execute("TRUNCATE TABLE raw.yolo_detections;")
        
        insert_query = """
            INSERT INTO raw.yolo_detections 
            (message_id, channel_name, detected_class, confidence_score, image_category, image_path)
            VALUES %s;
        """
        extras.execute_values(cursor, insert_query, records)
        conn.commit()
        logging.info(f"Successfully database-ingested {len(records)} computer vision rows into raw.yolo_detections!")
        
    except Exception as e:
        logging.error(f"Failed loading vision database asset: {str(e)}")
    finally:
        if 'conn' in locals() and conn: conn.close()

if __name__ == "__main__":
    load_yolo_csv_to_postgres()
    