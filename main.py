import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication

from ui.main_window import MainWindow
from ui.theme import apply_dark_theme


def main():
    app = QApplication(sys.argv)

    # 🔑 ОБОВʼЯЗКОВО для QSettings (БЕЗ ЦЬОГО НІЧОГО НЕ ЗБЕРІГАЄТЬСЯ)
    QCoreApplication.setOrganizationName("CryptoCombiner")
    QCoreApplication.setApplicationName("CryptoCombiner")

    # 🎨 Темна тема
    apply_dark_theme(app)

    # 🧱 DEBUG-рамки (тимчасово)
    app.setStyleSheet(app.styleSheet() + """
        QWidget#root { border: 1px solid #2C2C2C; }
        QWidget#content { border: 1px solid #3A3A3A; }
        QWidget#sidebar { border: 1px solid #444444; }
        QWidget#right { border: 1px solid #3A3A3A; }
        QWidget#tabsbar { border: 1px solid #555555; }
        QStackedWidget#pages { border: 1px dashed #666666; }
    """)

    window = MainWindow()
    window.show()

    # ⚠️ restore_state ПІСЛЯ show()
    window.restore_state()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
