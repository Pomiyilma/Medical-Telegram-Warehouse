#It creates and returns a connected Telethon client.

from telethon import TelegramClient
from src.config import API_ID, API_HASH, SESSION_NAME

client = TelegramClient(
    SESSION_NAME,
    API_ID,
    API_HASH
)
