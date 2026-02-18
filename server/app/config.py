import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
MODEL_STORAGE_PATH = os.getenv("MODEL_STORAGE_PATH", "models/")