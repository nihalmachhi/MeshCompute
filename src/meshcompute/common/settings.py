"""Validated runtime configuration loaded from environment variables."""
from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """One immutable source of service settings."""
    model_config = SettingsConfigDict(env_prefix="MESH_COMPUTE_", env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_name: str = "MeshCompute"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://meshcompute:meshcompute@localhost:5432/meshcompute"
    coordinator_url: str = "http://localhost:8000"
    data_dir: Path = Path("/data")
    lease_ttl_seconds: int = Field(default=30,ge=3)
    heartbeat_interval_seconds: int = Field(default=10,ge=1)
    reaper_interval_seconds: int = Field(default=5,ge=1)
    max_task_attempts: int = Field(default=3,ge=1)
    max_pending_tasks: int = Field(default=10_000,ge=1)
    task_timeout_seconds: int = Field(default=300,ge=1)
    worker_poll_interval_seconds: float = Field(default=1.0,ge=0.1)
    log_level: str = "INFO"
    @property
    def sync_database_url(self) -> str:
        """Return the synchronous psycopg URL used by SQLAlchemy."""
        return self.database_url.replace("postgresql://","postgresql+psycopg://",1) if self.database_url.startswith("postgresql://") else self.database_url

@lru_cache
def get_settings() -> Settings:
    """Return the process-wide validated settings object."""
    return Settings()
