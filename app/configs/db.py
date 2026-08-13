import duckdb
from app.configs.settings import settings

_connection = None

def get_db_connection():
    global _connection
    if _connection is None:
        _connection = duckdb.connect(settings.DB_PATH, read_only=settings.READ_ONLY)
    return _connection

def get_cursor():
    return get_db_connection().cursor()

def get_db():
    yield get_db_connection()