import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    PROJECT_NAME = "Text-to-SQL API"
    PORT = int(os.getenv("PORT", 8000))
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    DB_URL = os.getenv("DB_URL", DATABASE_URL)
    CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")

config = Config()
