import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    PROJECT_NAME = "Text-to-SQL API"
    PORT = int(os.getenv("PORT", 8000))
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/text2sql")
    DB_URL = os.getenv("DB_URL", DATABASE_URL)
    DB_TYPE = os.getenv("DB_TYPE", "mysql")
    # CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

config = Config()
