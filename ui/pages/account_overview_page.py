from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QScrollArea,
)
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QIcon, QPixmap
from ui.pages.base_page import BasePage


class AccountOverviewPage(BasePage):
    """Сторінка відображення балансів акаунту"""

    def __init__(self):
        super().__init__()
        self.settings = QSettings()
        self.binance_client = None
        self._setup_ui()
        self._load_account()

    def _setup_ui(self):
        """Створення інтерфейсу"""
        
        # ===== ЗАГОЛОВОК =====
        header_layout = QHBoxLayout()
        
        # Заголовок з піктограмою та назвою біржі
        title_container = QHBoxLayout()
        title_label = QLabel("Баланси акаунту")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_container.addWidget(title_label)
        
        # Іконка біржі
        self.exchange_icon = QLabel()
        self.exchange_icon.setFixedSize(24, 24)
        self.exchange_icon.setScaledContents(True)
        self.exchange_icon.setAlignment(Qt.AlignCenter)
        title_container.addWidget(self.exchange_icon)
        
        # Назва біржі
        self.exchange_label = QLabel()
        self.exchange_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #F0B90B;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin-left: 5px;
            }
        """)
        title_container.addWidget(self.exchange_label)
        title_container.addStretch()
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        self.refresh_btn = QPushButton("Оновити")
        self.refresh_btn.clicked.connect(self._load_account)
        header_layout.addWidget(self.refresh_btn)
        
        self._layout.addLayout(header_layout)

        # ===== СПОТ БАЛАНСИ =====
        self.spot_group = QGroupBox("Спот")
        self.spot_layout = QVBoxLayout(self.spot_group)
        self.spot_table = self._create_balances_table()
        self.spot_layout.addWidget(self.spot_table)
        self._layout.addWidget(self.spot_group)

        # ===== Ф'ЮЧЕРСИ =====
        self.futures_group = QGroupBox("Ф'ючерси")
        self.futures_layout = QVBoxLayout(self.futures_group)
        self.futures_table = self._create_balances_table()
        self.futures_layout.addWidget(self.futures_table)
        self._layout.addWidget(self.futures_group)

        # ===== МАРЖИНАЛЬНИЙ ТОРГ =====
        self.margin_group = QGroupBox("Маржинальний торг")
        self.margin_layout = QVBoxLayout(self.margin_group)
        self.margin_table = self._create_balances_table()
        self.margin_layout.addWidget(self.margin_table)
        self._layout.addWidget(self.margin_group)

        # ===== СТАТУС =====
        self.status_label = QLabel("Статус: Не підключено")
        self.status_label.setStyleSheet("color: #888888;")
        self._layout.addWidget(self.status_label)

        self._layout.addStretch()

    def _create_balances_table(self) -> QTableWidget:
        """Створює таблицю для відображення балансів"""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Актив", "Доступно", "В обробці", "Загалом"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                border: 1px solid #3A3A3A;
                gridline-color: #3A3A3A;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2C2C2C;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #FF8C66;
            }
        """)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        return table

    def _load_account(self):
        """Завантаження балансів з підключеного акаунту"""
        default_account = self.settings.value("account/default", "")
        
        if not default_account:
            self.status_label.setText("Статус: Акаунт не вибрано")
            self.exchange_icon.clear()
            self.exchange_label.setText("")
            self._clear_all_tables()
            return

        # Оновлюємо піктограму та назву біржі в заголовку
        self._update_exchange_display(default_account)

        if default_account == "Binance":
            self._load_binance_balances()
        else:
            self.status_label.setText(f"Статус: Підтримка {default_account} в розробці")
            self._clear_all_tables()

    def _load_binance_balances(self):
        """Завантаження балансів з Binance"""
        api_key = self.settings.value("exchanges/binance/api_key", "")
        secret_key = self.settings.value("exchanges/binance/secret_key", "")

        if not api_key or not secret_key:
            self.status_label.setText("Статус: Binance API не налаштовано")
            self._clear_all_tables()
            return

        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("Оновлення...")
        self.status_label.setText("Статус: Завантаження балансів...")

        try:
            from binance.client import Client
            
            client = Client(api_key, secret_key)
            self.binance_client = client

            # Завантажуємо баланси з різних типів
            self._load_spot_balances(client)
            self._load_futures_balances(client)
            self._load_margin_balances(client)

            self.status_label.setText("Статус: ✅ Баланси завантажено")
            
        except ImportError:
            self.status_label.setText("Статус: ⚠️ Бібліотека python-binance не встановлена")
            QMessageBox.warning(
                self,
                "Попередження",
                "Бібліотека python-binance не встановлена.\n\n"
                "Встановіть її командою:\npip install python-binance"
            )
            self._clear_all_tables()
        except Exception as e:
            error_msg = str(e)
            if "Invalid API-key" in error_msg:
                error_msg = "Невірний API Key"
            elif "Signature" in error_msg:
                error_msg = "Невірний Secret Key"
            
            self.status_label.setText(f"Статус: ❌ Помилка: {error_msg}")
            self._clear_all_tables()
            QMessageBox.critical(
                self,
                "Помилка",
                f"Не вдалося завантажити баланси:\n{error_msg}"
            )
        finally:
            self.refresh_btn.setEnabled(True)
            self.refresh_btn.setText("Оновити")

    def _load_spot_balances(self, client):
        """Завантаження спот балансів"""
        try:
            account = client.get_account()
            balances = [
                b for b in account['balances'] 
                if float(b['free']) > 0 or float(b['locked']) > 0
            ]
            
            self._populate_table(self.spot_table, balances)
        except Exception as e:
            self.spot_table.setRowCount(0)
            print(f"Помилка завантаження спот балансів: {e}")

    def _load_futures_balances(self, client):
        """Завантаження ф'ючерсних балансів"""
        try:
            # Отримуємо баланс ф'ючерсного акаунту
            futures_account = client.futures_account()
            assets = futures_account.get('assets', [])
            
            # Фільтруємо тільки активи з балансом
            balances = [
                {
                    'asset': a['asset'],
                    'free': a['availableBalance'],
                    'locked': a['marginBalance'],
                    'total': a['walletBalance']
                }
                for a in assets 
                if float(a.get('walletBalance', 0)) > 0
            ]
            
            self._populate_table(self.futures_table, balances)
        except Exception as e:
            self.futures_table.setRowCount(0)
            print(f"Помилка завантаження ф'ючерсних балансів: {e}")

    def _load_margin_balances(self, client):
        """Завантаження маржинальних балансів"""
        try:
            # Отримуємо баланс маржинального акаунту
            margin_account = client.get_margin_account()
            user_assets = margin_account.get('userAssets', [])
            
            # Форматуємо дані
            balances = [
                {
                    'asset': a['asset'],
                    'free': a['free'],
                    'locked': a['locked'],
                    'total': a['netAsset']
                }
                for a in user_assets 
                if float(a.get('netAsset', 0)) > 0
            ]
            
            self._populate_table(self.margin_table, balances)
        except Exception as e:
            self.margin_table.setRowCount(0)
            print(f"Помилка завантаження маржинальних балансів: {e}")

    def _get_human_readable_asset_name(self, asset: str) -> str:
        """Конвертує технічну назву активу в зрозумілу (людську)"""
        # Прибираємо префікси типу LD, L, тощо
        # Наприклад: LDBNB -> BNB, LDDOGE -> DOGE, LDERD -> ERD, LDHOME -> HOME
        if not asset:
            return asset
        
        # Прибираємо префікс "LD" (Liquid staking)
        if asset.startswith('LD'):
            return asset[2:]
        
        # Прибираємо префікс "L" якщо наступний символ велика літера
        if asset.startswith('L') and len(asset) > 1 and asset[1].isupper():
            return asset[1:]
        
        # Прибираємо інші поширені префікси
        prefixes = ['BUSD', 'USDT', 'USDC']  # Якщо актив починається з цих префіксів, залишаємо як є
        for prefix in prefixes:
            if asset.startswith(prefix) and len(asset) > len(prefix):
                # Якщо після префіксу є ще символи, це може бути складний актив
                pass
        
        return asset

    def _populate_table(self, table: QTableWidget, balances: list):
        """Заповнення таблиці балансами"""
        table.setRowCount(len(balances))
        
        for row, balance in enumerate(balances):
            asset = balance.get('asset', '')
            # Конвертуємо технічну назву в зрозумілу
            human_readable_asset = self._get_human_readable_asset_name(asset)
            free = float(balance.get('free', 0))
            locked = float(balance.get('locked', 0))
            total = float(balance.get('total', free + locked))
            
            # Актив (з "людською" назвою)
            asset_item = QTableWidgetItem(human_readable_asset)
            asset_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            # Зберігаємо оригінальну назву в userData для можливого використання
            asset_item.setData(Qt.UserRole, asset)
            table.setItem(row, 0, asset_item)
            
            # Доступно
            free_item = QTableWidgetItem(f"{free:.8f}".rstrip('0').rstrip('.'))
            free_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 1, free_item)
            
            # В обробці
            locked_item = QTableWidgetItem(f"{locked:.8f}".rstrip('0').rstrip('.'))
            locked_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 2, locked_item)
            
            # Загалом
            total_item = QTableWidgetItem(f"{total:.8f}".rstrip('0').rstrip('.'))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 3, total_item)
        
        # Сортуємо за активом
        table.sortItems(0, Qt.AscendingOrder)

    def _load_exchange_icon(self, exchange_name: str) -> QPixmap:
        """Завантажує іконку біржі"""
        import os
        from pathlib import Path
        
        # Шлях до папки з іконками
        base_path = Path(__file__).parent.parent.parent
        icons_path = base_path / "assets" / "icons"
        
        # Створюємо папку, якщо її немає
        icons_path.mkdir(parents=True, exist_ok=True)
        
        # Спробуємо різні варіанти назв файлів
        possible_names = [
            f"{exchange_name.lower()}.png",
            f"{exchange_name.lower()}.png.png",  # На випадок подвійного розширення
        ]
        
        for icon_name in possible_names:
            icon_file = icons_path / icon_name
            if icon_file.exists():
                pixmap = QPixmap(str(icon_file))
                if not pixmap.isNull():
                    scaled = pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    return scaled
        
        # Якщо іконки немає, повертаємо порожній pixmap
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        return pixmap

    def _update_exchange_display(self, exchange_name: str):
        """Оновлює піктограму та назву біржі в заголовку"""
        # Завантажуємо іконку біржі
        icon_pixmap = self._load_exchange_icon(exchange_name)
        self.exchange_icon.setPixmap(icon_pixmap)
        
        if exchange_name == "Binance":
            # Назва біржі
            self.exchange_label.setText("BINANCE")
            self.exchange_label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #F0B90B;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin-left: 5px;
                }
            """)
        else:
            # Для інших бірж
            self.exchange_label.setText(exchange_name.upper())
            self.exchange_label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #E0E0E0;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin-left: 5px;
                }
            """)

    def _clear_all_tables(self):
        """Очищення всіх таблиць"""
        self.spot_table.setRowCount(0)
        self.futures_table.setRowCount(0)
        self.margin_table.setRowCount(0)

