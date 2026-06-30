from telethon.tl.types import MessageMediaPhoto
from src.telegram_client import client

CHANNELS = [
    "CheMed123",     
    "lobelia4cosmetics",
    "Tikvahpharm"
]

#Below to conver telegram message obj into python dictionary
def extract_message(message, channel_name):
    return {
        "message_id": message.id,
        "channel_name": channel_name,
        "message_date": message.date.isoformat(),
        "message_text": message.message or "",
        "has_media": isinstance(message.media, MessageMediaPhoto),
        "image_path": None,
        "views": message.views or 0,
        "forwards": message.forwards or 0,
    }

#Scrape messages from 1 channel and return a list of message dictionaries
async def scrape_channel(channel_name, limit=100):
    messages_data = []

    async for message in client.iter_messages(channel_name, limit=limit):
        messages_data.append(
            extract_message(message, channel_name)
        )

    return messages_data

#Scrapes messages from all channels in the CHANNELS list and returns a dictionary with channel names as keys and lists of message dictionaries as values
async def scrape_all_channels(limit=100):
    all_data = {}

    for channel in CHANNELS:
        print(f"Scraping {channel}...")

        channel_messages = await scrape_channel(
            channel,
            limit
        )

        all_data[channel] = channel_messages

    return all_data



import asyncio


async def main():

    await client.start()

    data = await scrape_all_channels(limit=10)

    for channel, messages in data.items():
        print(f"\n{channel}")

        for message in messages[:3]:
            print(message)

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())