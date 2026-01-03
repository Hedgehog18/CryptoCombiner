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
        self.btn_settings = self._make_nav_btn("Налаштування")

        layout.addWidget(self.btn_overview)
        layout.addWidget(self.btn_trade)
        layout.addWidget(self.btn_settings)

        layout.addStretch(1)

        self.btn_overview.clicked.connect(lambda: self.section_changed.emit("Огляд"))
        self.btn_trade.clicked.connect(lambda: self.section_changed.emit("Trade"))
        self.btn_settings.clicked.connect(lambda: self.section_changed.emit("Налаштування"))

        # ===== TABS (створюються динамічно для кожного розділу) =====
        self.tab_group = QButtonGroup(self)
        self.tab_group.setExclusive(True)
        self.tab_group.idClicked.connect(self.top_tab_changed.emit)

        # Зберігаємо вкладки для кожного розділу
        self.overview_tabs = []
        self.trade_tabs = []
        self.settings_tabs = []

        # Створюємо вкладки для "Огляд"
        self.overview_tabs.append(self._make_tab_btn("Вкладка 1"))
        self.overview_tabs.append(self._make_tab_btn("Вкладка 2"))

        # Створюємо вкладки для "Trade"
        self.trade_tabs.append(self._make_tab_btn("Вкладка 1"))
        self.trade_tabs.append(self._make_tab_btn("Вкладка 2"))

        # Створюємо вкладки для "Налаштування"
        self.settings_tabs.append(self._make_tab_btn("Акаунт"))

        # default
        self.btn_overview.setChecked(True)
        # Ініціалізуємо вкладки для початкового розділу
        self._update_tab_group("Огляд")
        self.overview_tabs[0].setChecked(True)

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

    def _update_tab_group(self, section: str):
        """Оновлює QButtonGroup для поточного розділу"""
        # Очищаємо всі кнопки з групи
        for btn in self.tab_group.buttons():
            self.tab_group.removeButton(btn)

        # Додаємо вкладки для поточного розділу з правильними індексами
        tabs = []
        if section == "Огляд":
            tabs = self.overview_tabs
        elif section == "Trade":
            tabs = self.trade_tabs
        elif section == "Налаштування":
            tabs = self.settings_tabs

        for i, tab in enumerate(tabs):
            self.tab_group.addButton(tab, i)

    def create_top_tabs(self) -> QWidget:
        w = QWidget()
        self.tabs_layout = QHBoxLayout(w)
        self.tabs_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs_layout.setSpacing(10)
        return w

    def update_tabs_for_section(self, section: str):
        """Оновлює вкладки для поточного розділу"""
        # Оновлюємо QButtonGroup
        self._update_tab_group(section)

        # Очищаємо поточні вкладки з layout
        while self.tabs_layout.count():
            item = self.tabs_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Додаємо вкладки для поточного розділу
        tabs = []
        if section == "Огляд":
            tabs = self.overview_tabs
        elif section == "Trade":
            tabs = self.trade_tabs
        elif section == "Налаштування":
            tabs = self.settings_tabs

        for tab in tabs:
            self.tabs_layout.addWidget(tab)
        self.tabs_layout.addStretch(1)

    def set_active_section(self, name: str):
        if name == "Огляд":
            self.btn_overview.setChecked(True)
        elif name == "Trade":
            self.btn_trade.setChecked(True)
        elif name == "Налаштування":
            self.btn_settings.setChecked(True)

    def set_active_tab(self, index: int):
        btn = self.tab_group.button(index)
        if btn:
            btn.setChecked(True)
