from qie.config import settings


def test_project_name() -> None:
    assert settings.project_name == "Quant Intelligence Engine"


def test_data_directories() -> None:
    assert settings.data_dir.name == "data"
    assert settings.raw_data_dir.name == "raw"
    assert settings.processed_data_dir.name == "processed"
