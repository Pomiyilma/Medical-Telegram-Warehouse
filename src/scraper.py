import os
import json
import asyncio
import random
import logging
from datetime import datetime
from telethon.tl.types import MessageMediaPhoto
from src.telegram_client import client

# Configure logging to save into logs/scraper.log
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/scraper.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

CHANNELS = [
    "CheMed123",      
    "lobelia4cosmetics",
    "tikvahpharma"
]

# Ensure basic directories exist
DATA_DIR = "data/raw"
PHOTOS_DIR = "data/photos"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PHOTOS_DIR, exist_ok=True)

def extract_message(message, channel_name, image_path=None):
    return {
        "message_id": message.id,
        "channel_name": channel_name,
        "message_date": message.date.isoformat(),
        "message_text": message.message or "",
        "has_media": isinstance(message.media, MessageMediaPhoto),
        "image_path": image_path,
        "views": message.views or 0,
        "forwards": message.forwards or 0,
    }

async def scrape_channel(channel_name, limit=10):
    messages_data = []
    channel_photos_dir = os.path.join(PHOTOS_DIR, channel_name)
    os.makedirs(channel_photos_dir, exist_ok=True)

    logging.info(f"Starting extraction for channel: {channel_name}")
    
    try:
        async for message in client.iter_messages(channel_name, limit=limit):
            image_path = None
            
            # Check if message contains a photo and download safely
            if isinstance(message.media, MessageMediaPhoto):
                # Unique filename formatting: channel_messageID.jpg
                filename = f"{channel_name}_{message.id}.jpg"
                full_path = os.path.join(channel_photos_dir, filename)
                
                # Only download if we haven't downloaded it before
                if not os.path.exists(full_path):
                    logging.info(f"Downloading media for message {message.id} in {channel_name}...")
                    await client.download_media(message.media, file=full_path)
                    image_path = full_path
                else:
                    image_path = full_path

            # Extract details
            msg_dict = extract_message(message, channel_name, image_path)
            messages_data.append(msg_dict)
            
    except Exception as e:
        logging.error(f"Error scraping channel {channel_name}: {str(e)}")
        
    return messages_data

async def scrape_all_channels(limit=10):
    all_data = {}

    for channel in CHANNELS:
        channel_messages = await scrape_channel(channel, limit)
        all_data[channel] = channel_messages
        
        # ANTI-BAN GUARDRAIL: Rest between channel scraping hops
        sleep_time = random.uniform(3, 6)
        logging.info(f"Sleeping for {sleep_time:.2f}s to respect rate limits...")
        await asyncio.sleep(sleep_time)

    # Save the structured data into our raw data lake folder as JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = os.path.join(DATA_DIR, f"raw_scraped_data_{timestamp}.json")
    
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
        
    logging.info(f"Successfully saved raw data lake export to: {json_filename}")
    return all_data

async def main():
    logging.info("Connecting to Telegram...")
    await client.start()
    
    # Keeping limit=10 for absolute safe execution during testing
    await scrape_all_channels(limit=10)
    
    logging.info("Disconnecting from Telegram...")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
    