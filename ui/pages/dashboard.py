from PySide6.QtWidgets import QLabel
from ui.pages.base_page import BasePage


class DashboardPage(BasePage):
    def __init__(self, title: str):
        super().__init__()
        lbl = QLabel(title)
        self._layout.addWidget(lbl)
        self._layout.addStretch(1)
