from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


CONFIG_PATH = Path(__file__).resolve().with_name("app_state.json")


@dataclass(slots=True)
class AppConfig:
    is_monitoring_active: bool = True
    monitored_directories: list[str] = field(default_factory=list)


def normalize_directory(path: str) -> str:
    return str(Path(path).expanduser().resolve(strict=False))


def normalize_directories(paths: Iterable[str]) -> list[str]:
    unique_paths: list[str] = []
    seen: set[str] = set()
    for raw_path in paths:
        if not raw_path:
            continue
        normalized = normalize_directory(raw_path)
        if normalized in seen:
            continue
        seen.add(normalized)
        unique_paths.append(normalized)
    return unique_paths


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or CONFIG_PATH

    def load(self) -> AppConfig:
        if not self.path.exists():
            return AppConfig()

        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return AppConfig()

        directories = payload.get("monitored_directories", [])
        if not isinstance(directories, list):
            directories = []

        return AppConfig(
            is_monitoring_active=bool(payload.get("is_monitoring_active", True)),
            monitored_directories=normalize_directories(directories),
        )

    def save(self, config: AppConfig) -> None:
        payload = asdict(config)
        payload["monitored_directories"] = normalize_directories(config.monitored_directories)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temp_path.replace(self.path)
