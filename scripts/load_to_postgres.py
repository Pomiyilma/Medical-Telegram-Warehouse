import os
import json
import glob
import logging
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv

# Configure logging to print clear updates in the terminal
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

load_dotenv()

# Read the database settings we just put inside your .env file
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATA_DIR = "data/raw"

def get_latest_json_file(directory):
    """Finds the most recent JSON scraping file in your data folder."""
    search_path = os.path.join(directory, "raw_scraped_data_*.json")
    files = glob.glob(search_path)
    if not files:
        return None
    # Sort files by creation time to get the newest file
    return max(files, key=os.path.getctime)

def load_data_to_postgres():
    # Look for the JSON file you generated in Stage 1
    latest_file = get_latest_json_file(DATA_DIR)
    if not latest_file:
        logging.error("No raw scraped JSON files found in data/raw/. Did you run the scraper first?")
        return

    logging.info(f"Targeting raw data file: {latest_file}")
    
    # Open and read the JSON data lake file
    with open(latest_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Flatten the channel-grouped entries into a flat layout list
    flattened_records = []
    for channel_name, messages in raw_data.items():
        for msg in messages:
            flattened_records.append((
                msg["message_id"],
                msg["channel_name"],
                msg["message_date"],
                msg["message_text"],
                msg["has_media"],
                msg["image_path"],
                msg["views"],
                msg["forwards"]
            ))

    if not flattened_records:
        logging.warning("No message entries found inside the file.")
        return

    # Attempt to open a gateway connection to PostgreSQL
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # 1. Create a safe isolated 'raw' workspace schema container
        cursor.execute("CREATE SCHEMA IF NOT EXISTS raw;")
        
        # 2. Build the structural database table to hold the fields
        create_table_query = """
        CREATE TABLE IF NOT EXISTS raw.telegram_messages (
            id SERIAL PRIMARY KEY,
            message_id INT,
            channel_name VARCHAR(255),
            message_date TIMESTAMPTZ,
            message_text TEXT,
            has_media BOOLEAN,
            image_path TEXT,
            views INT,
            forwards INT,
            inserted_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        cursor.execute(create_table_query)
        
        # Clear out any previous records from old tests to prevent duplicated lines
        cursor.execute("TRUNCATE TABLE raw.telegram_messages;")

        # 3. Use an optimized fast bulk execution approach (execute_values)
        insert_query = """
        INSERT INTO raw.telegram_messages 
        (message_id, channel_name, message_date, message_text, has_media, image_path, views, forwards)
        VALUES %s;
        """
        
        logging.info(f"Bulk loading {len(flattened_records)} records into Postgres raw.telegram_messages table...")
        extras.execute_values(cursor, insert_query, flattened_records)
        
        # Save changes to the database permanently
        conn.commit()
        logging.info("Database ingestion successfully committed!")

    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
        logging.error(f"Failed to load data into PostgreSQL: {str(e)}")
    finally:
        # Safely shut down the database connections
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    load_data_to_postgres()
    