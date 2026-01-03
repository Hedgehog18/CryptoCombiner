from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QGroupBox,
    QMessageBox,
)
from PySide6.QtCore import QSettings, Signal
from ui.pages.base_page import BasePage


class AccountPage(BasePage):
    """Сторінка налаштувань акаунту та API підключень"""

    account_changed = Signal(str)  # Сигнал при зміні акаунту за замовчуванням

    def __init__(self):
        super().__init__()
        self.settings = QSettings()
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Створення інтерфейсу"""
        
        # ===== АКАУНТ ЗА ЗАМОВЧУВАННЯМ =====
        default_account_group = QGroupBox("Акаунт за замовчуванням")
        default_account_layout = QVBoxLayout(default_account_group)
        
        account_label = QLabel("Виберіть акаунт, який буде використовуватися за замовчуванням:")
        default_account_layout.addWidget(account_label)
        
        self.default_account_combo = QComboBox()
        self.default_account_combo.addItem("Немає", "")
        self.default_account_combo.currentIndexChanged.connect(self._on_default_account_changed)
        default_account_layout.addWidget(self.default_account_combo)
        
        self._layout.addWidget(default_account_group)

        # ===== ПІДКЛЮЧЕННЯ БІРЖ =====
        exchanges_group = QGroupBox("Підключення бірж")
        exchanges_layout = QVBoxLayout(exchanges_group)

        # Binance
        binance_group = QGroupBox("Binance")
        binance_layout = QVBoxLayout(binance_group)

        # API Key
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel("API Key:")
        api_key_label.setMinimumWidth(100)
        self.binance_api_key = QLineEdit()
        self.binance_api_key.setPlaceholderText("Введіть ваш Binance API Key")
        self.binance_api_key.setEchoMode(QLineEdit.Password)
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.binance_api_key, 1)
        binance_layout.addLayout(api_key_layout)

        # Secret Key
        secret_key_layout = QHBoxLayout()
        secret_key_label = QLabel("Secret Key:")
        secret_key_label.setMinimumWidth(100)
        self.binance_secret_key = QLineEdit()
        self.binance_secret_key.setPlaceholderText("Введіть ваш Binance Secret Key")
        self.binance_secret_key.setEchoMode(QLineEdit.Password)
        secret_key_layout.addWidget(secret_key_label)
        secret_key_layout.addWidget(self.binance_secret_key, 1)
        binance_layout.addLayout(secret_key_layout)

        # Кнопки
        binance_buttons_layout = QHBoxLayout()
        self.binance_test_btn = QPushButton("Перевірити підключення")
        self.binance_test_btn.clicked.connect(self._test_binance_connection)
        self.binance_save_btn = QPushButton("Зберегти")
        self.binance_save_btn.clicked.connect(self._save_binance_credentials)
        binance_buttons_layout.addWidget(self.binance_test_btn)
        binance_buttons_layout.addWidget(self.binance_save_btn)
        binance_buttons_layout.addStretch()
        binance_layout.addLayout(binance_buttons_layout)

        # Статус підключення
        self.binance_status_label = QLabel("Статус: Не підключено")
        binance_layout.addWidget(self.binance_status_label)

        exchanges_layout.addWidget(binance_group)
        self._layout.addWidget(exchanges_group)

        self._layout.addStretch()

    def _load_settings(self):
        """Завантаження збережених налаштувань"""
        # Завантажуємо акаунт за замовчуванням
        default_account = self.settings.value("account/default", "")
        self._update_accounts_list()
        
        # Встановлюємо вибраний акаунт
        index = self.default_account_combo.findData(default_account)
        if index >= 0:
            self.default_account_combo.setCurrentIndex(index)

        # Завантажуємо Binance credentials
        binance_api_key = self.settings.value("exchanges/binance/api_key", "")
        binance_secret = self.settings.value("exchanges/binance/secret_key", "")
        
        if binance_api_key:
            self.binance_api_key.setText(binance_api_key)
        if binance_secret:
            self.binance_secret_key.setText(binance_secret)

        # Оновлюємо статус
        if binance_api_key and binance_secret:
            self.binance_status_label.setText("Статус: Збережено (не перевірено)")
        else:
            self.binance_status_label.setText("Статус: Не підключено")

    def _update_accounts_list(self):
        """Оновлює список доступних акаунтів"""
        self.default_account_combo.clear()
        self.default_account_combo.addItem("Немає", "")

        # Отримуємо список збережених акаунтів
        accounts = self.settings.value("account/list", [])
        if isinstance(accounts, str):
            accounts = [accounts] if accounts else []
        elif not isinstance(accounts, list):
            accounts = []

        for account in accounts:
            if account:  # Перевіряємо, що акаунт не порожній
                self.default_account_combo.addItem(account, account)

    def _on_default_account_changed(self, index: int):
        """Обробник зміни акаунту за замовчуванням"""
        account_data = self.default_account_combo.currentData()
        if account_data:
            self.settings.setValue("account/default", account_data)
            self.account_changed.emit(account_data)
        else:
            self.settings.setValue("account/default", "")
            self.account_changed.emit("")

    def _save_binance_credentials(self):
        """Збереження Binance API credentials"""
        api_key = self.binance_api_key.text().strip()
        secret_key = self.binance_secret_key.text().strip()

        if not api_key or not secret_key:
            QMessageBox.warning(
                self,
                "Помилка",
                "Будь ласка, введіть API Key та Secret Key"
            )
            return

        # Зберігаємо credentials
        self.settings.setValue("exchanges/binance/api_key", api_key)
        self.settings.setValue("exchanges/binance/secret_key", secret_key)

        # Додаємо акаунт до списку, якщо його там немає
        accounts = self.settings.value("account/list", [])
        if isinstance(accounts, str):
            accounts = [accounts] if accounts else []
        elif not isinstance(accounts, list):
            accounts = []

        account_name = "Binance"
        if account_name not in accounts:
            accounts.append(account_name)
            self.settings.setValue("account/list", accounts)
            self._update_accounts_list()

        self.binance_status_label.setText("Статус: Збережено (не перевірено)")
        
        QMessageBox.information(
            self,
            "Успішно",
            "Налаштування Binance збережено!"
        )

    def _test_binance_connection(self):
        """Перевірка підключення до Binance API"""
        api_key = self.binance_api_key.text().strip()
        secret_key = self.binance_secret_key.text().strip()

        if not api_key or not secret_key:
            QMessageBox.warning(
                self,
                "Помилка",
                "Будь ласка, введіть API Key та Secret Key перед перевіркою"
            )
            return

        self.binance_test_btn.setEnabled(False)
        self.binance_test_btn.setText("Перевірка...")
        self.binance_status_label.setText("Статус: Перевірка підключення...")

        try:
            # Перевірка підключення через Binance API
            from binance.client import Client
            
            client = Client(api_key, secret_key)
            # Перевіряємо підключення, отримуючи інформацію про акаунт
            account_info = client.get_account()
            
            # Якщо успішно, отримуємо баланс
            balances = [b for b in account_info['balances'] if float(b['free']) > 0]
            
            self.binance_status_label.setText("Статус: ✅ Підключено успішно")
            QMessageBox.information(
                self,
                "Успішно",
                f"Підключення до Binance API успішне!\n\n"
                f"Знайдено {len(balances)} активних балансів."
            )
        except ImportError:
            self.binance_status_label.setText("Статус: ⚠️ Бібліотека не встановлена")
            QMessageBox.warning(
                self,
                "Попередження",
                "Бібліотека python-binance не встановлена.\n\n"
                "Встановіть її командою:\npip install python-binance"
            )
        except Exception as e:
            error_msg = str(e)
            # Спрощуємо повідомлення про помилку
            if "Invalid API-key" in error_msg or "API-key format invalid" in error_msg:
                error_msg = "Невірний API Key"
            elif "Signature" in error_msg or "signature" in error_msg:
                error_msg = "Невірний Secret Key"
            elif "IP" in error_msg or "whitelist" in error_msg.lower():
                error_msg = "IP адреса не додана до whitelist в налаштуваннях API"
            
            self.binance_status_label.setText("Статус: ❌ Помилка підключення")
            QMessageBox.critical(
                self,
                "Помилка",
                f"Не вдалося підключитися до Binance API:\n{error_msg}"
            )
        finally:
            self.binance_test_btn.setEnabled(True)
            self.binance_test_btn.setText("Перевірити підключення")

