@echo off
REM Skrypt do uruchomienia projektu EmAI Fraud Detection (Windows)

echo 🚀 Uruchamianie projektu EmAI Fraud Detection...

REM Sprawdź czy Python jest zainstalowany
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nie jest zainstalowany. Zainstaluj Python 3.8+
    pause
    exit /b 1
)

REM Sprawdź czy pip jest zainstalowany
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip nie jest zainstalowany. Zainstaluj pip
    pause
    exit /b 1
)

REM Utwórz środowisko wirtualne
echo 📦 Tworzenie środowiska wirtualnego...
python -m venv venv

REM Aktywuj środowisko wirtualne
echo 🔧 Aktywowanie środowiska wirtualnego...
call venv\Scripts\activate.bat

REM Zainstaluj zależności
echo 📚 Instalowanie zależności...
pip install -r requirements.txt

echo ✅ Instalacja zakończona!
echo.
echo 📋 Dostępne komendy:
echo   python main.py                    - Scraping danych z App Store/Google Play
echo   python pattern_discovery_analyzer.py - Analiza wzorców
echo   python build_model.py             - Budowanie modelu
echo   python evaluation.py              - Ocena modelu
echo   python predict_app.py             - Predykcja dla nowych aplikacji
echo.
echo 📖 Dokumentacja: README.md
pause
