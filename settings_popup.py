from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton, QKeySequenceEdit
)
from PySide6.QtCore import Qt
from configparser import ConfigParser

config = ConfigParser()
config.read("settings.ini")

class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setWindowFlags(Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # --- Hotkey ---
        hotkey_layout = QHBoxLayout()
        hotkey_label = QLabel("Shortcut (Win only):")
        self.hotkey_edit = QKeySequenceEdit()
        current_hotkey = config.get("General", "shortcut", fallback="Super+Space")
        self.hotkey_edit.setKeySequence(current_hotkey)
        hotkey_layout.addWidget(hotkey_label)
        hotkey_layout.addWidget(self.hotkey_edit)
        self.main_layout.addLayout(hotkey_layout)

        # --- Enable/disable commands ---
        self.command_checkboxes = {}
        for cmd, desc in [
            ("expression", "Expression"),
            ("conversion", "Conversion"),
            ("youtube", "YouTube search"),
            ("duckduckgo", "DuckDuckGo search"),
            ("wikipedia", "Wikipedia search"),
            ("perplexity", "Perplexity search")
        ]:
            cb = QCheckBox(desc)
            cb.setChecked(config.getboolean("Commands", cmd, fallback=True))
            self.command_checkboxes[cmd] = cb
            self.main_layout.addWidget(cb)

        # --- Save button ---
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        self.main_layout.addWidget(save_btn)

    def save_settings(self):
        # --- Save hotkey ---
        hotkey_str = self.hotkey_edit.keySequence().toString()
        if not config.has_section("General"):
            config.add_section("General")
        config.set("General", "shortcut", hotkey_str)

        # --- Save command toggles ---
        if not config.has_section("Commands"):
            config.add_section("Commands")
        for cmd, cb in self.command_checkboxes.items():
            config.set("Commands", cmd, str(cb.isChecked()))

        # --- Write config ---
        with open("settings.ini", "w") as f:
            config.write(f)
        self.destroy()
