from __future__ import annotations

from process_inspector.unity.infrastructure.factory import build_unity_path_service


def get_unity_path_service():
    return build_unity_path_service()
