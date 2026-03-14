from __future__ import annotations

import re
from pathlib import Path

SUBDOMAINS = [
    "appcontrol",
    "servicecontrol",
    "scriptcontrol",
    "oscontrol",
    "taskcontrol",
    "teamviewer",
    "unity",
]

BANNED_INFRA_IMPORT_SNIPPETS = [
    "import psutil",
    "from psutil",
    "import subprocess",
    "from subprocess",
    "import winreg",
    "from winreg",
]

IMPORT_RE = re.compile(
    r"^(?:from|import)\s+process_inspector\.(?P<subdomain>[a-z_]+)\.(?P<layer>[a-z_]+)",
    re.MULTILINE,
)


def _iter_python_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*.py") if path.is_file())


def _collect_layer_imports(content: str) -> list[tuple[str, str]]:
    return [
        (m.group("subdomain"), m.group("layer")) for m in IMPORT_RE.finditer(content)
    ]


def test_domain_and_application_layers_do_not_import_system_libraries():
    base = Path("src/process_inspector")
    violations: list[str] = []

    for subdomain in SUBDOMAINS:
        for layer in ("domain", "application"):
            layer_root = base / subdomain / layer
            for file_path in _iter_python_files(layer_root):
                content = file_path.read_text(encoding="utf-8")
                matches = [
                    f"{file_path}: {snippet}"
                    for snippet in BANNED_INFRA_IMPORT_SNIPPETS
                    if snippet in content
                ]
                violations.extend(matches)

    assert not violations, "Layer boundary violations:\n" + "\n".join(violations)


def test_domain_layer_import_direction():
    base = Path("src/process_inspector")
    violations: list[str] = []

    for subdomain in SUBDOMAINS:
        layer_root = base / subdomain / "domain"
        for file_path in _iter_python_files(layer_root):
            content = file_path.read_text(encoding="utf-8")
            for imported_subdomain, imported_layer in _collect_layer_imports(content):
                if imported_subdomain == subdomain and imported_layer == "domain":
                    continue
                violations.append(
                    f"{file_path}: imports process_inspector.{imported_subdomain}.{imported_layer}"
                )

    assert not violations, "Domain import direction violations:\n" + "\n".join(
        violations
    )


def test_application_layer_import_direction():
    base = Path("src/process_inspector")
    violations: list[str] = []
    allowed_layers = {"domain", "application"}

    for subdomain in SUBDOMAINS:
        layer_root = base / subdomain / "application"
        for file_path in _iter_python_files(layer_root):
            content = file_path.read_text(encoding="utf-8")
            for imported_subdomain, imported_layer in _collect_layer_imports(content):
                if imported_subdomain != subdomain:
                    violations.append(
                        f"{file_path}: cross-subdomain import process_inspector.{imported_subdomain}.{imported_layer}"
                    )
                    continue
                if imported_layer not in allowed_layers:
                    violations.append(
                        f"{file_path}: disallowed layer import process_inspector.{imported_subdomain}.{imported_layer}"
                    )

    assert not violations, "Application import direction violations:\n" + "\n".join(
        violations
    )


def test_servicecontrol_implementations_do_not_depend_on_interface_contracts():
    impl_root = Path("src/process_inspector/servicecontrol/implementations")
    violations: list[str] = []

    for file_path in _iter_python_files(impl_root):
        content = file_path.read_text(encoding="utf-8")
        if "process_inspector.servicecontrol.interface" in content:
            violations.append(str(file_path))

    assert not violations, "Implementations depend on interface layer:\n" + "\n".join(
        violations
    )


def test_unity_interface_init_is_not_backpointing_to_base_module():
    init_file = Path("src/process_inspector/unity/interface/__init__.py")
    content = init_file.read_text(encoding="utf-8")
    assert "process_inspector.unity.base" not in content


def test_interface_layer_do_not_import_system_libraries():
    base = Path("src/process_inspector")
    violations: list[str] = []

    for subdomain in SUBDOMAINS:
        layer_root = base / subdomain / "interface"
        for file_path in _iter_python_files(layer_root):
            content = file_path.read_text(encoding="utf-8")
            matches = [
                f"{file_path}: {snippet}"
                for snippet in BANNED_INFRA_IMPORT_SNIPPETS
                if snippet in content
            ]
            violations.extend(matches)

    assert not violations, "Interface boundary violations:\n" + "\n".join(violations)
