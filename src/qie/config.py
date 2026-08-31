from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Quant Intelligence Engine"
    environment: str = "development"

    project_root: Path = Path(__file__).resolve().parents[2]
    data_dir: Path = project_root / "data"
    raw_data_dir: Path = data_dir / "raw"
    interim_data_dir: Path = data_dir / "interim"
    processed_data_dir: Path = data_dir / "processed"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
