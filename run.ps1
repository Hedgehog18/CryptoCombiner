# PowerShell скрипт для швидкого запуску CryptoCombiner
Set-Location $PSScriptRoot
python main.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nПомилка запуску! Перевірте, чи встановлений Python та залежності." -ForegroundColor Red
    Write-Host "Встановіть залежності: pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Натисніть Enter для виходу"
}

