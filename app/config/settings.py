from dotenv import load_dotenv
import os

env_file_path = os.getcwd() + "/.env"

env_loaded = load_dotenv(dotenv_path=env_file_path, override=True)

TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH")

DB_TYPE = os.getenv("DB_TYPE")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_SCHEMA = os.getenv("DB_SCHEMA")