from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass(frozen=True, slots=True)
class Settings:
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    @property
    def db_dsn(self) -> str:
        return (
            f"host={self.db_host} "
            f"port={self.db_port} "
            f"dbname={self.db_name} "
            f"user={self.db_user} "
            f"password={self.db_password}"
        )
    
def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value.strip()

def get_settings() -> Settings:
    load_dotenv()

    db_host = _require_env("DB_HOST")
    db_port_raw = _require_env("DB_PORT")
    db_name = _require_env("DB_NAME")
    db_user = _require_env("DB_USER")
    db_password = _require_env("DB_PASSWORD")

    try:
        db_port = int(db_port_raw)
    except ValueError as exc:
        raise RuntimeError(f"DB_PORT must be an integer, got: {db_port_raw}") from exc
    
    return Settings(
        db_host=db_host,
        db_port=db_port,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
    )