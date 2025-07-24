#!/bin/bash
# Skrypt do uruchomienia projektu EmAI Fraud Detection

echo "🚀 Uruchamianie projektu EmAI Fraud Detection..."

# Sprawdź czy Python jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nie jest zainstalowany. Zainstaluj Python 3.8+"
    exit 1
fi

# Sprawdź czy pip jest zainstalowany
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 nie jest zainstalowany. Zainstaluj pip"
    exit 1
fi

# Utwórz środowisko wirtualne
echo "📦 Tworzenie środowiska wirtualnego..."
python3 -m venv venv

# Aktywuj środowisko wirtualne
echo "🔧 Aktywowanie środowiska wirtualnego..."
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Zainstaluj zależności
echo "📚 Instalowanie zależności..."
pip install -r requirements.txt

echo "✅ Instalacja zakończona!"
echo ""
echo "📋 Dostępne komendy:"
echo "  python main.py                    - Scraping danych z App Store/Google Play"
echo "  python pattern_discovery_analyzer.py - Analiza wzorców"
echo "  python build_model.py             - Budowanie modelu"
echo "  python evaluation.py              - Ocena modelu"
echo "  python predict_app.py             - Predykcja dla nowych aplikacji"
echo ""
echo "📖 Dokumentacja: README.md"
