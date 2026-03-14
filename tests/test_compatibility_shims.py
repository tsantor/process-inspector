from __future__ import annotations

from process_inspector.appcontrol.interface import AppInterface
from process_inspector.scriptcontrol.interface import ScriptInterface
from process_inspector.taskcontrol import ScheduledTask
from process_inspector.teamviewer.teamviewer import Teamviewer


def test_legacy_interface_imports_resolve():
    assert AppInterface.__name__ == "AppInterface"
    assert ScriptInterface.__name__ == "ScriptInterface"


def test_legacy_module_exports_remain_available():
    assert ScheduledTask.__name__ == "ScheduledTask"
    assert Teamviewer.__name__ == "Teamviewer"
