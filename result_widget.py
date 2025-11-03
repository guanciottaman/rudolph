from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt

class ResultWidget(QWidget):
    def __init__(self, name: str, description: str):
        super().__init__()

        layout = QVBoxLayout()

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Nome
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("""
            font-size: 16px;
            font-family: Montserrat;
            color: black;
            background-color: rgba(0,0,0,0);  /* trasparente */
        """)

        layout.addWidget(self.name_label)

        self.description_label = QLabel(description)
        self.description_label.setWordWrap(True)
        self.description_label.setMaximumWidth(550)
        self.description_label.setFixedWidth(580)
        self.description_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        self.description_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.description_label.setStyleSheet("""
            font-size: 16px;
            font-family: Montserrat;
            color: rgba(58, 51, 51, 1);
            background-color: rgba(0,0,0,0);
        """)
        layout.addWidget(self.description_label)

        self.setLayout(layout)
        self.adjustSize()


