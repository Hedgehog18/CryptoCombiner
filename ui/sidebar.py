from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QButtonGroup,
    QHBoxLayout,
)


class Sidebar(QWidget):
    top_tab_changed = Signal(int)
    section_changed = Signal(str)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # ===== SECTIONS =====
        self.section_group = QButtonGroup(self)
        self.section_group.setExclusive(True)

        self.btn_overview = self._make_nav_btn("Огляд")
        self.btn_trade = self._make_nav_btn("Trade")

        layout.addWidget(self.btn_overview)
        layout.addWidget(self.btn_trade)

        layout.addStretch(1)

        self.btn_overview.clicked.connect(lambda: self.section_changed.emit("Огляд"))
        self.btn_trade.clicked.connect(lambda: self.section_changed.emit("Trade"))

        # ===== TABS =====
        self.tab_group = QButtonGroup(self)
        self.tab_group.setExclusive(True)

        self.tab1 = self._make_tab_btn("Вкладка 1")
        self.tab2 = self._make_tab_btn("Вкладка 2")

        self.tab_group.addButton(self.tab1, 0)
        self.tab_group.addButton(self.tab2, 1)

        self.tab_group.idClicked.connect(self.top_tab_changed.emit)

        # default
        self.btn_overview.setChecked(True)
        self.tab1.setChecked(True)

    # ===== FACTORIES =====

    def _make_nav_btn(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("navBtn")
        btn.setCheckable(True)
        self.section_group.addButton(btn)
        return btn

    def _make_tab_btn(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("tabBtn")
        btn.setCheckable(True)
        return btn

    # ===== API =====

    def create_top_tabs(self) -> QWidget:
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        row.addWidget(self.tab1)
        row.addWidget(self.tab2)
        row.addStretch(1)

        return w

    def set_active_section(self, name: str):
        if name == "Огляд":
            self.btn_overview.setChecked(True)
        elif name == "Trade":
            self.btn_trade.setChecked(True)

    def set_active_tab(self, index: int):
        btn = self.tab_group.button(index)
        if btn:
            btn.setChecked(True)
