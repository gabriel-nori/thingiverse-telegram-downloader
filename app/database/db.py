from app.config import settings
import sqlite3

class Database:
    db_type: str = settings.DB_TYPE

    def __init__(self) -> None:
        match self.db_type:
            case "sqlite":
                pass
            case "postgres":
                pass