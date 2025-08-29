import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("8369183040:AAFWREA6Nhz9P6opj4d5zJiw2k5OnwWcfYk")
    BOT_USERNAME = os.getenv("WhispeyBot")  # Without @
    DATA_FILE = os.getenv("DATA_FILE", "data/whispers.json")
    OWNER_ID = 8429156335
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
