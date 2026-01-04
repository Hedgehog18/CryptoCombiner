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
        
        # ===== SCROLL AREA ДЛЯ КОНТЕНТУ =====
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Контейнер для контенту всередині scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(15)
        
        self._content_layout = content_layout  # Зберігаємо для додавання груп

        # ===== ОГЛЯД (всі баланси) =====
        self.overview_group = QGroupBox("Огляд")
        self.overview_layout = QVBoxLayout(self.overview_group)
        self.overview_table = self._create_balances_table()
        self.overview_layout.addWidget(self.overview_table)
        self._content_layout.addWidget(self.overview_group)

        # ===== EARN =====
        self.earn_group = QGroupBox("Earn")
        self.earn_layout = QVBoxLayout(self.earn_group)
        self.earn_table = self._create_balances_table()
        self.earn_layout.addWidget(self.earn_table)
        self._content_layout.addWidget(self.earn_group)

        # ===== СПОТ БАЛАНСИ =====
        self.spot_group = QGroupBox("Спот")
        self.spot_layout = QVBoxLayout(self.spot_group)
        self.spot_table = self._create_balances_table()
        self.spot_layout.addWidget(self.spot_table)
        self._content_layout.addWidget(self.spot_group)

        # ===== Ф'ЮЧЕРСИ =====
        self.futures_group = QGroupBox("Ф'ючерси")
        self.futures_layout = QVBoxLayout(self.futures_group)
        self.futures_table = self._create_balances_table()
        self.futures_layout.addWidget(self.futures_table)
        self._content_layout.addWidget(self.futures_group)

        # ===== ПОПОВНЕННЯ (FUNDING) =====
        self.funding_group = QGroupBox("Поповнення")
        self.funding_layout = QVBoxLayout(self.funding_group)
        self.funding_table = self._create_balances_table()
        self.funding_layout.addWidget(self.funding_table)
        self._content_layout.addWidget(self.funding_group)

        # ===== СТАТУС =====
        self.status_label = QLabel("Статус: Не підключено")
        self.status_label.setStyleSheet("color: #888888;")
        self._content_layout.addWidget(self.status_label)

        # Встановлюємо контент у scroll area
        scroll_area.setWidget(content_widget)
        
        # Додаємо scroll area до основного layout
        self._layout.addWidget(scroll_area)

    def _create_balances_table(self) -> QTableWidget:
        """Створює таблицю для відображення балансів"""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Актив", "Доступно", "В обробці", "Загалом", "Вартість в USDT"])
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
        
        # Налаштування для автоматичного розміру
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.verticalHeader().setVisible(False)  # Приховуємо номери рядків
        
        # Встановлюємо мінімальну висоту для таблиці
        table.setMinimumHeight(100)
        
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

            # Отримуємо всі ціни один раз для оптимізації
            self.status_label.setText("Статус: Отримання цін...")
            all_assets = set()
            
            # Спочатку збираємо всі активи з усіх категорій
            spot_balances = self._load_spot_balances_raw(client)
            earn_balances = self._load_earn_balances_raw(client)
            futures_balances = self._load_futures_balances_raw(client)
            funding_balances = self._load_funding_balances_raw(client)
            
            # Збираємо всі унікальні активи
            for balance_list in [spot_balances, earn_balances, futures_balances, funding_balances]:
                for balance in balance_list:
                    asset = balance.get('asset', '')
                    if asset:
                        all_assets.add(asset)
            
            # Очищаємо кеш тикерів перед новим завантаженням
            if hasattr(self, '_all_tickers_cache'):
                delattr(self, '_all_tickers_cache')
            
            # Отримуємо ціни для всіх активів одним запитом
            self._price_cache = self._get_all_prices(list(all_assets), client)
            
            # Тепер завантажуємо баланси з використанням кешу цін
            self.status_label.setText("Статус: Завантаження балансів...")
            
            # Завантажуємо баланси для кожної категорії (без обмеження кількості)
            sorted_spot = self._get_sorted_balances(spot_balances, client)
            sorted_earn = self._get_sorted_balances(earn_balances, client)
            sorted_futures = self._get_sorted_balances(futures_balances, client)
            sorted_funding = self._get_sorted_balances(funding_balances, client)
            
            self._populate_table(self.spot_table, sorted_spot, client)
            self._populate_table(self.earn_table, sorted_earn, client)
            self._populate_table(self.futures_table, sorted_futures, client)
            self._populate_table(self.funding_table, sorted_funding, client)
            
            # Огляд - об'єднуємо всі баланси
            all_balances = self._combine_balances([
                spot_balances,
                earn_balances,
                futures_balances,
                funding_balances
            ])
            sorted_overview = self._get_sorted_balances(all_balances, client)
            self._populate_table(self.overview_table, sorted_overview, client)

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

    def _load_spot_balances_raw(self, client):
        """Завантаження спот балансів (без Earn активів) - без обробки"""
        try:
            account = client.get_account()
            # Спот баланси - це баланси без префіксів LD, L (Earn активи)
            balances = [
                {
                    'asset': b['asset'],
                    'free': b['free'],
                    'locked': b['locked'],
                    'total': str(float(b['free']) + float(b['locked']))
                }
                for b in account['balances'] 
                if (float(b['free']) > 0 or float(b['locked']) > 0) and
                   not b['asset'].startswith('LD') and
                   not (b['asset'].startswith('L') and len(b['asset']) > 1 and b['asset'][1].isupper())
            ]
            return balances
        except Exception as e:
            print(f"Помилка завантаження спот балансів: {e}")
            return []

    def _load_earn_balances_raw(self, client):
        """Завантаження Earn балансів - без обробки"""
        try:
            account = client.get_account()
            # Earn активи зазвичай мають префікс LD (Liquid Staking) або L з великої літери
            balances = [
                {
                    'asset': b['asset'],
                    'free': b['free'],
                    'locked': b['locked'],
                    'total': str(float(b['free']) + float(b['locked']))
                }
                for b in account['balances'] 
                if (float(b['free']) > 0 or float(b['locked']) > 0) and
                   (b['asset'].startswith('LD') or 
                    (b['asset'].startswith('L') and len(b['asset']) > 1 and b['asset'][1].isupper()))
            ]
            return balances
        except Exception as e:
            print(f"Помилка завантаження Earn балансів: {e}")
            return []

    def _load_futures_balances_raw(self, client):
        """Завантаження ф'ючерсних балансів - без обробки"""
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
            return balances
        except Exception as e:
            print(f"Помилка завантаження ф'ючерсних балансів: {e}")
            return []

    def _load_funding_balances_raw(self, client):
        """Завантаження балансів поповнення (Funding) - без обробки"""
        try:
            # Funding баланси - це баланси на ф'ючерсному акаунті, які не використовуються для торгівлі
            # Використовуємо futures_account і беремо availableBalance як funding
            futures_account = client.futures_account()
            assets = futures_account.get('assets', [])
            
            # Funding - це активи, які доступні, але не заблоковані в позиціях
            balances = [
                {
                    'asset': a['asset'],
                    'free': a['availableBalance'],
                    'locked': '0',
                    'total': a['availableBalance']
                }
                for a in assets 
                if float(a.get('availableBalance', 0)) > 0
            ]
            return balances
        except Exception as e:
            print(f"Помилка завантаження балансів поповнення: {e}")
            return []

    def _combine_balances(self, balance_lists: list) -> list:
        """Об'єднує баланси з різних категорій, підсумовуючи однакові активи"""
        combined = {}
        
        for balance_list in balance_lists:
            if not balance_list:
                continue
            for balance in balance_list:
                asset = balance.get('asset', '')
                if not asset:
                    continue
                
                try:
                    # Обробляємо free
                    free_str = balance.get('free', '0')
                    free = float(free_str) if isinstance(free_str, str) else float(free_str)
                    
                    # Обробляємо locked
                    locked_str = balance.get('locked', '0')
                    locked = float(locked_str) if isinstance(locked_str, str) else float(locked_str)
                    
                    # Обробляємо total
                    total_str = balance.get('total', '0')
                    if isinstance(total_str, str):
                        total = float(total_str) if total_str else (free + locked)
                    else:
                        total = float(total_str) if total_str else (free + locked)
                    
                    # Якщо total = 0, обчислюємо з free + locked
                    if total == 0:
                        total = free + locked
                    
                    if asset in combined:
                        # Підсумовуємо баланси для того ж активу
                        combined[asset]['free'] = str(float(combined[asset]['free']) + free)
                        combined[asset]['locked'] = str(float(combined[asset]['locked']) + locked)
                        combined[asset]['total'] = str(float(combined[asset]['total']) + total)
                    else:
                        combined[asset] = {
                            'asset': asset,
                            'free': str(free),
                            'locked': str(locked),
                            'total': str(total)
                        }
                except (ValueError, TypeError) as e:
                    print(f"Помилка обробки балансу {asset}: {e}, balance={balance}")
                    continue
        
        return list(combined.values())

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

    def _get_all_prices(self, assets: list, client) -> dict:
        """Отримує ціни для всіх активів ефективно через batch запит"""
        prices = {}
        if not client or not assets:
            return prices
        
        try:
            # Отримуємо всі тикери одним запитом (кешуємо результат)
            if not hasattr(self, '_all_tickers_cache'):
                self._all_tickers_cache = client.get_all_tickers()
            
            ticker_dict = {t['symbol']: float(t['price']) for t in self._all_tickers_cache}
            
            # Для кожного активу шукаємо пару USDT
            for asset in assets:
                human_readable = self._get_human_readable_asset_name(asset)
                
                # Для USDT повертаємо 1.0
                if human_readable.upper() == "USDT":
                    prices[asset] = 1.0
                    continue
                
                # Спробуємо знайти пару з USDT
                symbol = f"{human_readable}USDT"
                if symbol in ticker_dict:
                    prices[asset] = ticker_dict[symbol]
                else:
                    # Спробуємо через BUSD
                    symbol_busd = f"{human_readable}BUSD"
                    if symbol_busd in ticker_dict:
                        prices[asset] = ticker_dict[symbol_busd]
                    else:
                        # Спробуємо через BTC
                        symbol_btc = f"{human_readable}BTC"
                        if symbol_btc in ticker_dict and "BTCUSDT" in ticker_dict:
                            prices[asset] = ticker_dict[symbol_btc] * ticker_dict["BTCUSDT"]
                        else:
                            prices[asset] = 0.0
        except Exception as e:
            print(f"Помилка отримання цін: {e}")
            # Якщо не вдалося отримати batch, повертаємо порожній dict
        
        return prices

    def _get_sorted_balances(self, balances: list, client) -> list:
        """Повертає всі баланси, відсортовані за вартістю в USDT (від більшого до меншого)"""
        if not balances:
            return []
        
        if not client:
            # Якщо немає клієнта, повертаємо баланси як є (відсортовані за активом)
            return sorted(balances, key=lambda x: x.get('asset', ''))
        
        # Використовуємо кеш цін, якщо він є
        if hasattr(self, '_price_cache'):
            prices = self._price_cache
        else:
            # Якщо кешу немає, отримуємо ціни
            unique_assets = list(set([b.get('asset', '') for b in balances if b.get('asset')]))
            prices = self._get_all_prices(unique_assets, client)
        
        # Обчислюємо вартість для кожного балансу
        balances_with_value = []
        for balance in balances:
            asset = balance.get('asset', '')
            if not asset:
                continue
                
            try:
                free = float(balance.get('free', 0))
                locked = float(balance.get('locked', 0))
                total_str = balance.get('total', '0')
                if isinstance(total_str, str):
                    total = float(total_str) if total_str else (free + locked)
                else:
                    total = float(total_str) if total_str else (free + locked)
                
                if total == 0:
                    total = free + locked
                
                # Показуємо всі баланси, навіть якщо total == 0 (може бути дуже малий баланс)
            except (ValueError, TypeError) as e:
                print(f"Помилка обробки балансу {asset}: {e}")
                continue
            
            # Отримуємо ціну з кешу
            price_usdt = prices.get(asset, 0.0)
            if price_usdt == 0.0:
                # Якщо не знайдено в кеші, спробуємо отримати окремо
                price_usdt = self._get_asset_price_usdt(asset, client)
            
            value_usdt = total * price_usdt
            
            balances_with_value.append({
                'balance': balance,
                'value_usdt': value_usdt
            })
        
        # Сортуємо за вартістю (від більшого до меншого)
        balances_with_value.sort(key=lambda x: x['value_usdt'], reverse=True)
        
        # Повертаємо всі баланси (без обмеження)
        return [item['balance'] for item in balances_with_value]

    def _populate_table(self, table: QTableWidget, balances: list, client=None):
        """Заповнення таблиці балансами"""
        table.setRowCount(len(balances))
        
        # Використовуємо збережений клієнт, якщо не передано
        if client is None:
            client = self.binance_client
        
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
            
            # Вартість в USDT
            if client:
                price_usdt = self._get_asset_price_usdt(asset, client)
                value_usdt = total * price_usdt
                if value_usdt > 0:
                    if value_usdt < 0.01:
                        value_text = f"{value_usdt:.6f}".rstrip('0').rstrip('.')
                    elif value_usdt < 1:
                        value_text = f"{value_usdt:.4f}".rstrip('0').rstrip('.')
                    else:
                        value_text = f"{value_usdt:,.2f}".rstrip('0').rstrip('.')
                    value_item = QTableWidgetItem(value_text)
                else:
                    value_item = QTableWidgetItem("—")
            else:
                value_item = QTableWidgetItem("—")
            value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 4, value_item)
        
        # Сортуємо за активом
        table.sortItems(0, Qt.AscendingOrder)
        
        # Завжди дозволяємо прокрутку та адаптивну висоту
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Встановлюємо оптимальну висоту рядків
        if table.rowCount() > 0:
            table.resizeRowsToContents()
            
            # Встановлюємо мінімальну висоту (щоб було видно хоча б 3-4 рядки)
            header_height = table.horizontalHeader().height()
            row_height = table.rowHeight(0) if table.rowCount() > 0 else 30
            min_rows = min(3, table.rowCount())
            min_height = header_height + (row_height * min_rows)
            table.setMinimumHeight(min_height)
        else:
            table.setMinimumHeight(100)
        
        # Не встановлюємо максимальну висоту - дозволяємо таблиці адаптуватися до розміру контейнера
        table.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX

    def _get_asset_price_usdt(self, asset: str, client) -> float:
        """Отримує поточну ціну активу в USDT"""
        try:
            # Конвертуємо технічну назву в зрозумілу для пошуку пари
            human_readable = self._get_human_readable_asset_name(asset)
            
            # Для USDT повертаємо 1.0
            if human_readable.upper() == "USDT":
                return 1.0
            
            # Спробуємо знайти пару з USDT
            symbol = f"{human_readable}USDT"
            ticker = client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            # Якщо не знайдено пару USDT, спробуємо через BUSD або BTC
            try:
                # Спробуємо BUSD
                symbol = f"{human_readable}BUSD"
                ticker = client.get_symbol_ticker(symbol=symbol)
                price_busd = float(ticker['price'])
                # Конвертуємо BUSD в USDT (зазвичай 1:1)
                return price_busd
            except:
                try:
                    # Спробуємо через BTC
                    symbol_btc = f"{human_readable}BTC"
                    ticker_btc = client.get_symbol_ticker(symbol=symbol_btc)
                    price_btc = float(ticker_btc['price'])
                    
                    # Отримуємо ціну BTC в USDT
                    btc_usdt = client.get_symbol_ticker(symbol="BTCUSDT")
                    btc_price = float(btc_usdt['price'])
                    
                    return price_btc * btc_price
                except:
                    # Якщо не вдалося отримати ціну, повертаємо 0
                    return 0.0

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
        self.overview_table.setRowCount(0)
        self.earn_table.setRowCount(0)
        self.spot_table.setRowCount(0)
        self.futures_table.setRowCount(0)
        self.funding_table.setRowCount(0)

