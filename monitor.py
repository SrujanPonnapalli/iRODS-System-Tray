from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import ObservedWatch


class EventBridge(QObject):
    file_event = Signal(str, str, bool)
    monitor_error = Signal(str)


class IngestionEventHandler(FileSystemEventHandler):
    def __init__(self, bridge: EventBridge) -> None:
        super().__init__()
        self.bridge = bridge

    def on_any_event(self, event: FileSystemEvent) -> None:
        self.bridge.file_event.emit(event.event_type, event.src_path, event.is_directory)


class MonitorManager(QObject):
    file_event = Signal(str, str, bool)
    monitor_error = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._observer: Observer | None = None
        self._bridge = EventBridge()
        self._handler = IngestionEventHandler(self._bridge)
        self._bridge.file_event.connect(self.file_event.emit)
        self._bridge.monitor_error.connect(self.monitor_error.emit)
        self._watches: dict[str, ObservedWatch] = {}

    def sync(self, directories: list[str], is_active: bool) -> None:
        if not is_active:
            self.stop()
            return

        if not self._ensure_running():
            return

        expected = set(directories)
        for directory, watch in list(self._watches.items()):
            if directory in expected:
                continue
            try:
                self._observer.unschedule(watch)
            except KeyError:
                pass
            del self._watches[directory]

        for directory in directories:
            if directory in self._watches:
                continue
            if not Path(directory).is_dir():
                continue
            try:
                watch = self._observer.schedule(self._handler, directory, recursive=False)
            except OSError as exc:
                self.monitor_error.emit(f"Failed to watch {directory}: {exc}")
                continue
            self._watches[directory] = watch

    def stop(self) -> None:
        if self._observer is None:
            return

        self._observer.stop()
        self._observer.join(timeout=5)
        self._observer = None
        self._watches.clear()

    def shutdown(self) -> None:
        self.stop()

    def _ensure_running(self) -> bool:
        if self._observer is not None and self._observer.is_alive():
            return True

        try:
            self._observer = Observer()
            self._observer.start()
        except OSError as exc:
            self._observer = None
            self.monitor_error.emit(f"Failed to start background monitor: {exc}")
            return False

        return True
