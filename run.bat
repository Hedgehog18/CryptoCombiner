@echo off
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo Помилка запуску! Перевірте, чи встановлений Python та залежності.
    echo Встановіть залежності: pip install -r requirements.txt
    pause
)

