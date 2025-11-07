from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QApplication, QSizePolicy, QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt, QObject, QThread, Signal, QTimer
from PySide6.QtGui import QShortcut, QIcon, QAction, QCursor
from keyboard import add_hotkey


import sys
import os
import signal
import numexpr
import platform
import webbrowser
import requests
from configparser import ConfigParser
import re
import math

from result_widget import ResultWidget
from settings_popup import SettingsWindow
from units_formatted import UNITS


config = ConfigParser()
config.read("settings.ini")

shortcut = config.get("General", "shortcut", fallback="super+space")
max_history = config.getint("General", "max_history", fallback=50)

expression_enabled = config.getboolean("Commands", "expression", fallback=True)
conversion_enabled = config.getboolean("Commands", "conversion", fallback=True)
temp_enabled = config.getboolean("Commands", "temp", fallback=True)
youtube_search = config.getboolean("Commands", "youtube", fallback=True)
google_search = config.getboolean("Commands", "google", fallback=True)
duckduckgo_search = config.getboolean("Commands", "duckduckgo", fallback=True)
wikipedia_search = config.getboolean("Commands", "wikipedia", fallback=True)
perplexity_search = config.getboolean("Commands", "perplexity", fallback=True)


HEADERS = {
    "User-Agent": "WikipediaFetcher/1.0 (https://github.com/guanciottaman/wiki-fetcher)"
}


signal.signal(signal.SIGINT, signal.SIG_DFL)


def safe_eval(expr: str) -> str:
    try:
        expr = re.sub(r'(\d+(?:\.\d+)?)°', lambda m: f'({float(m.group(1))}*pi/180)', expr)
        local_dict = {
            "pi": math.pi,
            "e": math.e
        }
        return str(numexpr.evaluate(expr, local_dict))
    except Exception:
        return "Invalid expression"


class WeatherWorker(QObject):
    finished = Signal(str)
    def __init__(self, city:str) -> None:
        super().__init__()
        self.city = city
    
    def run(self):
        r = requests.get(f"https://wttr.in/{self.city}?format=%t+%C")
        self.finished.emit(r.text)


class WikipediaWorker(QObject):
    finished = Signal(str)
    def __init__(self, element:str) -> None:
        super().__init__()
        self.element = element

    def run(self):
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{self.element.strip().replace(" ", "_")}",
            headers=HEADERS
        )
        data = r.json()
        self.finished.emit(data["extract"])


class Launcher(QWidget):
    def __init__(self):
        super().__init__(
            parent=None,
            f=Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )

        self.threads = []
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), "assets", "icons", "icon.png")))

        self.tray_icon = QSystemTrayIcon(QIcon(os.path.join(os.getcwd(), "assets", "icons", "icon.png")), self)
        self.tray_icon.setToolTip("Rudolph Launcher")

        menu = QMenu()
        open_action = QAction("Open / Hide", self)
        open_action.triggered.connect(self.toggle)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)

        menu.addAction(open_action)
        menu.addSeparator()
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)

        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Type something...")
        self.entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(40, 40, 40, 0.95);
                color: white;
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 18px;
                font-family: Montserrat;
            }
        """)
        self.entry.textChanged.connect(self.process_query)

        self.settings_icon_path = os.path.join(os.getcwd(), "assets", "icons", "settings.png")
        self.settings_action = QAction(QIcon(self.settings_icon_path), "", self.entry)
        self.settings_action.triggered.connect(self.open_settings)
        self.entry.addAction(self.settings_action, QLineEdit.ActionPosition.TrailingPosition)

        self.main_layout.addWidget(self.entry)

        self.content = QWidget()
        self.setStyleSheet("""
            background-color: rgba(175, 184, 182, 0.95);
            margin: 0;
            padding: 0;
            border-radius: 10px;
        """)

        self.content_layout = QVBoxLayout()
        self.content.setLayout(self.content_layout)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(5)
        self.content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.main_layout.addWidget(self.content)

        self.resize(600, 60)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.center().x() - 300, screen.center().y() - 30)

        with open("command_history.txt", "r") as f:
            self.commands = f.readlines()

        self.history_up_shortcut = QShortcut(Qt.Key.Key_Up, self)
        self.history_up_shortcut.activated.connect(self.up_history)

        self.history_down_shortcut = QShortcut(Qt.Key.Key_Down, self)
        self.history_down_shortcut.activated.connect(self.down_history)

        self.history_index = None

        self.command_map = {
            "e": ("expression", lambda args: self.solve_expression(' '.join(args))),
            "c": ("conversion", lambda args: self.convert_measure(float(args[0]), args[1], args[2])
                    if len(args) == 3 else None),
            "temp": ("temp", lambda args: self.city_weather(' '.join(args))),
            "yt": ("youtube", lambda args: webbrowser.open(f"https://youtube.com/search?q={' '.join(args)}")),
            "ddg": ("duckduckgo", lambda args: webbrowser.open(f"https://duckduckgo.com/search?q={' '.join(args)}")),
            "wiki": ("wikipedia", lambda args: webbrowser.open(f"https://en.wikipedia.org/wiki/{'_'.join(args)}")),
            "wikisum": ("wikipedia", lambda args: self.wiki_summary('_'.join(args))),
            "plx": ("perplexity", lambda args: webbrowser.open(f"https://www.perplexity.ai/search?q={' '.join(args)}")),
        }

        self.entry.returnPressed.connect(self.hide)
        self.entry.focusOutEvent = lambda _: self.hide()
        self.setLayout(self.main_layout)

    def on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            QTimer.singleShot(50, self.toggle)

    
    def open_settings(self):
        if hasattr(self, "settings_window") and self.settings_window is not None:
            try:
                self.settings_window.close()
                self.settings_window.deleteLater()
            except:
                pass

        self.settings_window = SettingsWindow(parent=self)
        self.settings_window.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint
        )
        self.settings_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
    
    def reg_command(self, command:str):
        self.commands.append(command)
        with open("command_history.txt", "a") as f:
            f.write(command + "\n")
        self.history_index = None
    
    def up_history(self):
        if not self.commands:
            return

        if self.history_index is None:
            self.history_index = len(self.commands) - 1
        elif self.history_index > 0:
            self.history_index -= 1

        self.entry.setText(self.commands[self.history_index])

    def down_history(self):
        if not self.commands or self.history_index is None:
            return

        if self.history_index < len(self.commands) - 1:
            self.history_index += 1
            self.entry.setText(self.commands[self.history_index])
        else:
            self.history_index = None
            self.entry.clear()

    
    def solve_expression(self, expr: str) -> None:
        solved_expression = str(safe_eval(expr))
        if solved_expression == "Invalid expression":
            return
        self.content_layout.addWidget(ResultWidget("Expression", solved_expression))
    
    def convert_measure(self, n:float, start_unit:str, end_unit:str) -> None:
        for _, units in UNITS.items():
            if start_unit in units and end_unit in units[start_unit]:
                conversion = units[start_unit][end_unit]
                if callable(conversion):
                    result = conversion(n)
                else:
                    result = n * conversion
                self.content_layout.addWidget(
                    ResultWidget("Conversion", f"{round(result, 3)} {end_unit}")
                )
                return
            
    def _on_done(self, result: str):
        self.loading_widget.description_label.setText(result)
        self.loading_widget.adjustSize()
        self.content.adjustSize()
        self.adjustSize()


    def city_weather(self, city: str):
        self.loading_widget = ResultWidget(f"City Weather - {city}", "Loading...")
        self.content_layout.addWidget(self.loading_widget)

        worker = WeatherWorker(city)
        thread = QThread()
        worker.moveToThread(thread)

        worker.finished.connect(self._on_done)
        worker.finished.connect(thread.quit)

        thread.started.connect(worker.run)
        thread.start()
        
        self.threads.append((thread, worker))

    def wiki_summary(self, element: str):
        self.loading_widget = ResultWidget(f"Wikipedia Summary - {element}", "Loading...")
        self.content_layout.addWidget(self.loading_widget)

        worker = WikipediaWorker(element)
        thread = QThread()
        worker.moveToThread(thread)

        worker.finished.connect(self._on_done)
        worker.finished.connect(thread.quit)

        thread.started.connect(worker.run)
        thread.start()
        
        self.threads.append((thread, worker))

    def process_query(self, text: str):
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        if text:
            parts = text.split()
            cmd = parts[0]
            args = parts[1:]

            if cmd in self.command_map:
                setting_name, func = self.command_map[cmd]
                if config.getboolean("Commands", setting_name):
                    if cmd in ("e", "c"):
                        func(args)
                    elif text.endswith("  "):
                        self.reg_command(text[:-1])
                        func(args)
                    

    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            QTimer.singleShot(50, lambda: (
                self.raise_(),
                self.activateWindow(),
                self.entry.setFocus()
            ))



app = QApplication(sys.argv)
app.setDesktopFileName("rudolph.desktop")
app.setWindowIcon(QIcon.fromTheme("rudolph"))
launcher = Launcher()
launcher.toggle()

if platform.system() == "Linux":
    from PySide6.QtCore import QTimer
    import os

    TRIGGER_PATH = "/tmp/launcher_trigger"

    def check_trigger():
        if os.path.exists(TRIGGER_PATH):
            try:
                os.remove(TRIGGER_PATH)
            except FileNotFoundError:
                pass
            launcher.toggle()

    trigger_timer = QTimer()
    trigger_timer.timeout.connect(check_trigger)
    trigger_timer.start(100)
elif platform.system() == "Windows":
    add_hotkey(shortcut, launcher.toggle)

sys.exit(app.exec())
