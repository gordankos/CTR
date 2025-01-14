
from PySide6.QtCore import QObject, Signal


class EventManager(QObject):
    """
    Singleton-based event manager for cross-module communication.

    Class provides a centralized mechanism to emit and handle signals, reducing
    coupling between modules and ensuring that only one instance of the EventManager
    exists across the application

    Signals:
        - on_data_changed       - Emitted when any CTR data gets changed, used for unsaved data tracking
        - on_catalogue_update   - Emitted when a catalogue item gets changed, requiring other GUI elements update
        - on_recipe_update      - Emitted when a recipe gets changed, requiring other GUI elements update
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Method enforces existence of only one instance of the EventManager.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    on_data_changed = Signal(str)
    on_catalogue_update = Signal()
    on_recipe_update = Signal()

    def emit_data_changed(self, data: str | None = None):
        self.on_data_changed.emit(data)


_event_manager = None


def event_manager() -> EventManager:
    """
    Initialization function for the event manager instance.
    """
    global _event_manager
    if _event_manager is None:
        _event_manager = EventManager()
        print(f"Initializing EventManager ID {id(_event_manager)}")
    return _event_manager
