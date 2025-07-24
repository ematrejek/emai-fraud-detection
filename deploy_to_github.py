#!/usr/bin/env python3
"""
Skrypt do automatycznego utworzenia repozytorium GitHub i przeniesienia plików projektu EmAI Fraud Detection
"""

import os
import subprocess
import shutil
import json
from pathlib import Path

def run_command(command, cwd=None):
    """Wykonuje komendę w terminalu i zwraca wynik"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
        if result.returncode != 0:
            print(f"Błąd wykonania komendy: {command}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return False

def create_gitignore():
    """Tworzy plik .gitignore dla projektu Python"""
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.novnc/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
*.joblib
*.csv
*.png
*.jpg
*.jpeg
*.gif
*.pdf
log/
temp/
output/
results/

# Keep only essential data files
!training_dataset.csv
!patterns_for_model.json
!xgb_model.joblib
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print("✓ Utworzono plik .gitignore")

def create_requirements_txt():
    """Tworzy plik requirements.txt z zależnościami"""
    requirements_content = """pandas>=1.5.0
numpy>=1.21.0
xgboost>=1.6.0
scikit-learn>=1.1.0
google-play-scraper>=1.2.0
itunes-app-scraper-dmi>=0.9.6
thefuzz>=0.19.0
matplotlib>=3.5.0
seaborn>=0.11.0
joblib>=1.1.0
requests>=2.28.0
urllib3>=1.26.0
six>=1.16.0
"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    print("✓ Utworzono plik requirements.txt")

def get_essential_files():
    """Zwraca listę plików, które powinny być w repozytorium"""
    essential_files = [
        'main.py',
        'pattern_discovery_analyzer.py',
        'build_model.py',
        'evaluation.py',
        'predict_app.py',
        'keywords_analyzer.py',
        'suspicion_scorer_assessment.py',
        'README.md',
        'requirements.txt',
        '.gitignore',
        'Project Brief & Detailed Methodology.md'
    ]
    
    # Sprawdź, które pliki istnieją
    existing_files = []
    for file in essential_files:
        if os.path.exists(file):
            existing_files.append(file)
        else:
            print(f"⚠️  Plik {file} nie istnieje")
    
    return existing_files

def create_deployment_script():
    """Tworzy skrypt do łatwego uruchomienia projektu"""
    deploy_script = """#!/bin/bash
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
# venv\\Scripts\\activate  # Windows

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
"""
    
    with open('deploy.sh', 'w', encoding='utf-8') as f:
        f.write(deploy_script)
    
    # Nadaj uprawnienia do wykonywania (Linux/Mac)
    if os.name != 'nt':  # Nie Windows
        os.chmod('deploy.sh', 0o755)
    
    print("✓ Utworzono skrypt deploy.sh")

def create_windows_batch():
    """Tworzy plik .bat dla Windows"""
    batch_content = """@echo off
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
call venv\\Scripts\\activate.bat

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
"""
    
    with open('deploy.bat', 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print("✓ Utworzono skrypt deploy.bat")

def setup_git_repository():
    """Konfiguruje repozytorium Git"""
    print("\n🔧 Konfiguracja repozytorium Git...")
    
    # Inicjalizuj Git
    if not run_command("git init"):
        return False
    
    # Dodaj wszystkie pliki
    if not run_command("git add ."):
        return False
    
    # Pierwszy commit
    if not run_command('git commit -m "Initial commit: EmAI Fraud Detection System"'):
        return False
    
    print("✓ Repozytorium Git skonfigurowane")
    return True

def push_to_existing_repository():
    """Wypycha kod do istniejącego repozytorium na GitHubie"""
    print("\n🌐 Wypychanie kodu do istniejącego repozytorium...")
    
    # Sprawdź czy gh CLI jest zainstalowany
    if not run_command("gh --version"):
        print("❌ GitHub CLI (gh) nie jest zainstalowany.")
        print("Zainstaluj GitHub CLI: https://cli.github.com/")
        return False
    
    # Sprawdź czy użytkownik jest zalogowany
    if not run_command("gh auth status"):
        print("❌ Nie jesteś zalogowany do GitHub CLI.")
        print("Zaloguj się: gh auth login")
        return False
    
    # Dodaj remote do istniejącego repozytorium
    repo_url = "https://github.com/ematrejek/emai-fraud-detection.git"
    
    # Usuń istniejący remote jeśli istnieje
    run_command("git remote remove origin")
    
    # Dodaj nowy remote
    if not run_command(f'git remote add origin {repo_url}'):
        print(f"❌ Nie udało się dodać remote: {repo_url}")
        return False
    
    # Wypchnij kod do repozytorium
    if run_command("git push -u origin main"):
        print(f"✓ Kod został pomyślnie wypchnięty do: {repo_url}")
        return True
    else:
        print("❌ Nie udało się wypchnąć kodu automatycznie.")
        print("Wykonaj ręcznie:")
        print(f"git remote add origin {repo_url}")
        print("git push -u origin main")
        return False

def main():
    """Główna funkcja skryptu"""
    print("🚀 Skrypt wdrażania EmAI Fraud Detection do istniejącego repozytorium GitHub")
    print("=" * 60)
    
    # Sprawdź czy jesteśmy w odpowiednim katalogu
    if not os.path.exists('main.py'):
        print("❌ Nie jesteś w katalogu projektu EmAI.")
        print("Przejdź do katalogu z plikami projektu i uruchom skrypt ponownie.")
        return
    
    # Utwórz pliki konfiguracyjne
    print("\n📝 Tworzenie plików konfiguracyjnych...")
    create_gitignore()
    create_requirements_txt()
    create_deployment_script()
    create_windows_batch()
    
    # Sprawdź pliki
    print("\n📋 Sprawdzanie plików projektu...")
    essential_files = get_essential_files()
    print(f"✓ Znaleziono {len(essential_files)} plików do przeniesienia")
    
    # Konfiguruj Git
    if not setup_git_repository():
        print("❌ Nie udało się skonfigurować Git")
        return
    
    # Wypchnij kod do istniejącego repozytorium GitHub
    if push_to_existing_repository():
        print("\n🎉 Projekt został pomyślnie wdrożony na GitHub!")
        print("\n📋 Następne kroki:")
        print("1. Sprawdź repozytorium: https://github.com/ematrejek/emai-fraud-detection")
        print("2. Skonfiguruj GitHub Pages (opcjonalnie)")
        print("3. Dodaj collaborators (opcjonalnie)")
        print("4. Skonfiguruj GitHub Actions (opcjonalnie)")
    else:
        print("\n⚠️  Projekt został przygotowany lokalnie.")
        print("Wypchnij kod ręcznie:")
        print("git remote add origin https://github.com/ematrejek/emai-fraud-detection.git")
        print("git push -u origin main")

if __name__ == "__main__":
    main() 