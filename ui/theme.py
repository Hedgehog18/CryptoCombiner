from PySide6.QtWidgets import QApplication


def apply_dark_theme(app: QApplication):
    app.setStyleSheet("""
        QWidget {
            background-color: #1E1E1E;
            color: #E0E0E0;
            font-size: 13px;
        }

        QPushButton {
            background-color: #2C2C2C;
            border-radius: 6px;
            padding: 6px 12px;
        }

        QPushButton:hover {
            background-color: #3A3A3A;
        }

        QPushButton:checked {
            background-color: #505050;
        }

        QPushButton#navBtn:checked {
            background-color: #444444;
        }

        QPushButton#tabBtn:checked {
            background-color: #FF8C66;
            color: black;
        }

        QLineEdit {
            background-color: #2C2C2C;
            border: 1px solid #3A3A3A;
            border-radius: 4px;
            padding: 6px 8px;
        }

        QLineEdit:focus {
            border: 1px solid #FF8C66;
        }

        QComboBox {
            background-color: #2C2C2C;
            border: 1px solid #3A3A3A;
            border-radius: 4px;
            padding: 6px 8px;
        }

        QComboBox:hover {
            background-color: #3A3A3A;
        }

        QComboBox:focus {
            border: 1px solid #FF8C66;
        }

        QGroupBox {
            border: 1px solid #3A3A3A;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }

        QLabel {
            color: #E0E0E0;
        }
    """)
