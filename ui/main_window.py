from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
)
from PySide6.QtCore import QSettings

from ui.sidebar import Sidebar
from ui.pages.dashboard import DashboardPage
from ui.pages.account_page import AccountPage
from ui.pages.account_overview_page import AccountOverviewPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Crypto Combiner")

        # 🔑 QSettings (тепер namespace коректний)
        self.settings = QSettings()

        # ===== ROOT =====
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        # ===== CONTENT =====
        content = QWidget()
        content.setObjectName("content")
        root_layout.addWidget(content, 1)

        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(12)

        # ===== SIDEBAR =====
        self.sidebar = Sidebar()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        content_layout.addWidget(self.sidebar)

        # ===== RIGHT =====
        right = QWidget()
        right.setObjectName("right")
        content_layout.addWidget(right, 1)

        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(12)

        # ===== TABS =====
        self.tabsbar = self.sidebar.create_top_tabs()
        self.tabsbar.setObjectName("tabsbar")
        right_layout.addWidget(self.tabsbar)

        # ===== STACK =====
        self.section_stack = QStackedWidget()
        right_layout.addWidget(self.section_stack, 1)

        # ===== SECTIONS =====
        self.account_overview_page = AccountOverviewPage()
        self.overview_pages = QStackedWidget()
        self.overview_pages.addWidget(self.account_overview_page)
        self.overview_pages.addWidget(DashboardPage("Огляд: вкладка 2"))

        self.trade_pages = QStackedWidget()
        self.trade_pages.addWidget(DashboardPage("Trade: вкладка 1"))
        self.trade_pages.addWidget(DashboardPage("Trade: вкладка 2"))

        self.account_page = AccountPage()
        self.settings_pages = QStackedWidget()
        self.settings_pages.addWidget(self.account_page)
        
        # Підключаємо сигнал зміни акаунту для оновлення балансів
        self.account_page.account_changed.connect(self._on_account_changed)

        self.section_stack.addWidget(self.overview_pages)    # index 0
        self.section_stack.addWidget(self.trade_pages)       # index 1
        self.section_stack.addWidget(self.settings_pages)    # index 2

        # ===== STATE =====
        self.current_section = "Огляд"
        self.last_tab_index = {
            "Огляд": 0,
            "Trade": 0,
            "Налаштування": 0,
        }

        # ===== SIGNALS =====
        self.sidebar.top_tab_changed.connect(self.on_tab_changed)
        self.sidebar.section_changed.connect(self.on_section_changed)

    # ------------------------------------------------------------------
    # UI LOGIC
    # ------------------------------------------------------------------

    def on_tab_changed(self, index: int):
        self.last_tab_index[self.current_section] = index

        if self.current_section == "Огляд":
            self.overview_pages.setCurrentIndex(index)
        elif self.current_section == "Trade":
            self.trade_pages.setCurrentIndex(index)
        elif self.current_section == "Налаштування":
            self.settings_pages.setCurrentIndex(index)

    def on_section_changed(self, section: str):
        self.current_section = section

        if section == "Огляд":
            self.section_stack.setCurrentIndex(0)
        elif section == "Trade":
            self.section_stack.setCurrentIndex(1)
        elif section == "Налаштування":
            self.section_stack.setCurrentIndex(2)

        # Оновлюємо вкладки для поточного розділу
        self.sidebar.update_tabs_for_section(section)

        self.restore_tab_for_section(section)

    def restore_tab_for_section(self, section: str):
        index = self.last_tab_index.get(section, 0)

        self.sidebar.set_active_section(section)
        self.sidebar.set_active_tab(index)

        if section == "Огляд":
            self.overview_pages.setCurrentIndex(index)
        elif section == "Trade":
            self.trade_pages.setCurrentIndex(index)
        elif section == "Налаштування":
            self.settings_pages.setCurrentIndex(index)

    # ------------------------------------------------------------------
    # PERSISTENCE
    # ------------------------------------------------------------------

    def restore_state(self):
        """ВИКЛИКАЄТЬСЯ ПІСЛЯ show()"""

        # geometry
        geometry = self.settings.value("window/geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)

        # maximized
        if self.settings.value("window/maximized", False, bool):
            self.showMaximized()

        # ui state
        self.current_section = self.settings.value(
            "ui/current_section", "Огляд"
        )

        self.last_tab_index["Огляд"] = int(
            self.settings.value("ui/overview_tab", 0)
        )
        self.last_tab_index["Trade"] = int(
            self.settings.value("ui/trade_tab", 0)
        )
        self.last_tab_index["Налаштування"] = int(
            self.settings.value("ui/settings_tab", 0)
        )

        # Ініціалізуємо вкладки для початкового розділу
        self.sidebar.update_tabs_for_section(self.current_section)

        self.on_section_changed(self.current_section)

    def closeEvent(self, event):
        """ЗБЕРЕЖЕННЯ СТАНУ"""

        self.settings.setValue("window/geometry", self.saveGeometry())
        self.settings.setValue("window/maximized", self.isMaximized())

        self.settings.setValue("ui/current_section", self.current_section)
        self.settings.setValue("ui/overview_tab", self.last_tab_index["Огляд"])
        self.settings.setValue("ui/trade_tab", self.last_tab_index["Trade"])
        self.settings.setValue("ui/settings_tab", self.last_tab_index["Налаштування"])

        super().closeEvent(event)

    def _on_account_changed(self, account: str):
        """Обробник зміни акаунту за замовчуванням"""
        # Оновлюємо баланси на сторінці огляду
        if hasattr(self, 'account_overview_page'):
            self.account_overview_page._load_account()

    def _on_account_changed(self, account: str):
        """Обробник зміни акаунту за замовчуванням"""
        # Оновлюємо баланси на сторінці огляду
        if hasattr(self, 'account_overview_page'):
            self.account_overview_page._load_account()
