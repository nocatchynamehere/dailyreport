from __future__ import annotations
import psycopg
from src.config.settings import Settings

def get_connection(settings: Settings) -> psycopg.Connection:
    return psycopg.connect(settings.db_dsn, autocommit=True)