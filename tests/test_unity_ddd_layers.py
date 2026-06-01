from __future__ import annotations

from process_inspector.unity.infrastructure.path_service import UnityPathService
from process_inspector.unity.infrastructure.repository import read_text_file


def test_unity_path_service_variations_include_expected_forms():
    service = UnityPathService()
    values = service.get_developer_variations("X Studios")

    assert "X Studios" in values
    assert "XStudios" in values
    assert "x studios" in values


def test_unity_path_service_build_config_path(tmp_path):
    service = UnityPathService()
    config_path = service.build_config_path(tmp_path / "StreamingAssets")
    assert str(config_path).endswith("config.json")


def test_read_text_file_missing_returns_empty_string(tmp_path):
    missing = tmp_path / "missing.txt"
    assert read_text_file(missing) == ""


def test_read_text_file_reads_existing_file(tmp_path):
    path = tmp_path / "version.txt"
    path.write_text("1.2.3\n", encoding="utf8")
    assert read_text_file(path) == "1.2.3"
