"""Unit tests for RecentFilesRegistry."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSettings

from atlantis.core.settings import RECENT_FILES_KEY
from atlantis.model.recent_files import RecentFilesRegistry


def _isolated_registry(tmp_path: Path, limit: int = 10) -> RecentFilesRegistry:
    settings = QSettings("AtlantisTest", f"recent-{tmp_path.name}")
    settings.clear()
    return RecentFilesRegistry(limit=limit, settings=settings)


def test_add_promotes_to_front(tmp_path: Path) -> None:
    registry = _isolated_registry(tmp_path)
    first = tmp_path / "one.mmd"
    second = tmp_path / "two.mmd"
    registry.add(first)
    registry.add(second)
    registry.add(first)
    paths = registry.paths()
    assert paths[0] == str(first)
    assert paths[1] == str(second)


def test_prune_missing_drops_ghost_entries(tmp_path: Path) -> None:
    settings = QSettings("AtlantisTest", f"recent-prune-{tmp_path.name}")
    settings.clear()
    registry = RecentFilesRegistry(settings=settings)
    real = tmp_path / "real.mmd"
    real.write_text("graph LR\nA-->B", encoding="utf-8")
    ghost = tmp_path / "ghost.mmd"
    settings.setValue(RECENT_FILES_KEY, [str(real), str(ghost)])
    removed = registry.prune_missing()
    assert removed == 1
    assert str(real) in registry.paths()
    assert str(ghost) not in registry.paths()


def test_clear_empties_list(tmp_path: Path) -> None:
    registry = _isolated_registry(tmp_path)
    registry.add(tmp_path / "a.mmd")
    registry.clear()
    assert registry.paths() == []


def test_limit_truncates_entries(tmp_path: Path) -> None:
    registry = _isolated_registry(tmp_path, limit=2)
    for index in range(4):
        registry.add(tmp_path / f"{index}.mmd")
    assert len(registry.paths()) == 2
