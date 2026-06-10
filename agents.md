agents.md: System Tray Data Ingestion Application
Role & Objective

You are an expert Python software architect and senior PySide6 developer. Your task is to build a minimal, modern system tray application that monitors local directories for data ingestion using watchdog. The system must decouple the background monitoring service from the GUI configuration window, ensuring monitoring continues even when the GUI window is closed.
Technical Stack

    GUI & System Tray: PySide6

    File System Monitoring: watchdog

    Threading/Concurrency: PySide6.QtCore.QThread or QThreadPool (to keep the GUI responsive and isolation of file system events)

    Configuration Storage: json (local config file to persist monitored folders and application state)

Architectural Requirements
1. Separation of Concerns & State

    Core Application Class (QApplication): Must manage the application lifetime. The application must not quit when the last window is closed (QApplication.setQuitOnLastWindowClosed(False)).

    Background Worker (QThread / watchdog.observers.Observer): The file system observer must run on its own thread or via standard watchdog observer threads. Closing the settings GUI must not stop or destroy this observer loop.

    State Management: Maintain a centralized configuration state tracking:

        is_monitoring_active (boolean toggle)

        monitored_directories (list of strings representing paths)

2. System Tray Interface (QSystemTrayIcon)

    Icon: Use standard fallback system icons (e.g., QStyle.SP_ComputerIcon or a clean procedural icon) if no custom asset is provided.

    Interaction: Left-clicking or double-clicking the tray icon must toggle the visibility of the Settings GUI.

    Context Menu (Right-Click): Must contain at least the following actions:

        Open Settings: Shows/raises the GUI.

        Toggle Monitoring: A checkable menu item to turn file monitoring on/off globally without opening the GUI.

        Exit: Fully stops all watchdog observers, saves configurations, and exits the application (sys.exit()).

3. Settings & Directory GUI (QWidget or QMainWindow)

    Design: Clean, modern, minimalist. Use layouts (QVBoxLayout, QHBoxLayout) and clean spacing.

    Global Toggle: A prominent toggle switch or button at the top to enable/disable background file monitoring globally.

    Directory Management List:

        A list view showing all currently monitored folder paths.

        An "Add Folder" button opening a native directory selection dialog (QFileDialog.getExistingDirectory).

        A "Remove Folder" button (or context action) to delete the selected directory from the monitoring list.

    Window Behavior: Closing the window via the "X" button must merely hide it (self.hide()), not quit the application.

Implementation Details & Constraints

    Watchdog Integration: Dynamic modification of paths is required. When a user adds or removes a folder in the GUI, the background observer must safely update its streams (unschedule/schedule paths) without requiring an application restart.

    Thread Safety: Ensure any events captured by watchdog handlers that need to update the GUI use PySide6 Signals (Signals and Slots) to pass data safely across threads.

    Config Persistence: Automatically save the configuration JSON whenever folders are added/removed or the monitoring state is toggled. Load this configuration on startup to resume the previous state.

Project Structure Blueprint

Generate the code following a clean single-file layout or modular structure:

    config.py: Handles loading/saving monitored directory arrays and active flags.

    monitor.py: Contains the watchdog event handler subclass and helper classes to manage scheduling.

    ui.py: Contains the main settings window layout.

    tray.py: Coordinates the system tray, configuration interaction, and integration between the background threads and the UI.

    main.py: Main execution entry point.

Expected Output Deliverable

Provide well-documented, clean, object-oriented Python code implementing this system. Ensure code includes proper error handling for invalid or missing directories.