# EmAI Fraud Detection - Zaawansowany System Wykrywania Podejrzanych Aplikacji Mobilnych

## 📋 Przegląd Projektu

Projekt EmAI Fraud Detection to zaawansowany system klasyfikacji aplikacji mobilnych, który automatycznie identyfikuje podejrzane lub niskiej jakości aplikacje. System wykorzystuje **zaawansowane reguły scoringu** oparte na analizie słów kluczowych, progach wieku i pobrań, oraz inteligentnej obsłudze brakujących danych.

## 🎯 Cel Projektu

Głównym celem jest stworzenie zautomatyzowanego narzędzia klasyfikującego, które przypisuje **prawdopodobieństwo bycia suspicious** aplikacjom na podstawie zaawansowanych reguł i publicznie dostępnych danych.

## 🏗️ Architektura Systemu

System składa się z **4 głównych modułów**, które tworzą kompletny pipeline przetwarzania danych:

### 1. Wzbogacanie Danych (`enrich_data.py`)
- **Cel**: Pobieranie i wzbogacanie danych o aplikacjach z Google Play i App Store
- **Funkcjonalność**:
  - Scraping danych z obu sklepów aplikacji
  - Obliczanie wieku aplikacji w dniach
  - Konwersja liczby pobrań na wartości numeryczne
  - Łączenie z oryginalnymi danymi treningowymi

### 2. Budowanie Reguł (`build_rules.py`)
- **Cel**: Tworzenie zaawansowanych reguł scoringu na podstawie analizy danych
- **Funkcjonalność**:
  - **Analiza TF-IDF**: Identyfikacja najbardziej różnicujących słów kluczowych
  - **40 słów kluczowych**: Ranking i ważenie słów w nazwach aplikacji i domenach
  - **Optymalne progi**: Automatyczne znajdowanie progów dla wieku i pobrań
  - **Skalowanie prawdopodobieństw**: Najlepsze słowo = 100%, każde kolejne coraz mniej

### 3. Audyt Próbki (`audit_sample.py`)
- **Cel**: Klasyfikacja aplikacji w czasie rzeczywistym z zaawansowaną logiką
- **Funkcjonalność**:
  - **Inteligentny scoring**: Im więcej słów kluczowych, tym wyższe prawdopodobieństwo
  - **Obsługa brakujących danych**: 50% prawdopodobieństwo dla brakujących informacji
  - **Ważenie cech**: Różne wagi dla różnych typów cech
  - **Reguły biznesowe**: Specjalna obsługa aplikacji iOS i niedostępnych danych

### 4. Analiza Wpływu Progów (`analyze_threshold_impact.py`)
- **Cel**: Analiza wpływu różnych progów filtrowania na metryki biznesowe
- **Funkcjonalność**:
  - **Analiza CTR**: Obliczanie wpływu na Click-Through Rate
  - **Metryki biznesowe**: Analiza spend, konwersji, impressions
  - **Optymalizacja progów**: Znajdowanie optymalnego balansu między filtrowaniem a wydajnością
  - **Raportowanie**: Szczegółowe raporty dla różnych progów

## 🔧 Szczegółowy Proces Użycia

### Krok 1: Wzbogacanie Danych
```bash
python enrich_data.py
```
**Wymagania**: Plik `training_dataset.csv` z kolumnami `app_id` i `label`
**Wynik**: Plik `enriched_dataset.csv` z dodatkowymi kolumnami

### Krok 2: Budowanie Reguł
```bash
python build_rules.py
```
**Wymagania**: Plik `enriched_dataset.csv` z wzbogaconymi danymi
**Wynik**: Plik `advanced_rules.json` z regułami scoringu

### Krok 3: Audyt Próbki
```bash
python audit_sample.py
```
**Wymagania**: Plik `53755.csv` z kolumną `app_id` i reguły z poprzedniego kroku
**Wynik**: Plik `audit_results-53755.csv` z wynikami klasyfikacji

### Krok 4: Analiza Wpływu
```bash
python analyze_threshold_impact.py
```
**Wymagania**: Wyniki audytu i dane o wydajności
**Wynik**: Szczegółowa analiza wpływu różnych progów na metryki biznesowe

## 🚀 Zaawansowana Logika Scoringu

### 1. Słowa Kluczowe z Ważeniem
- **40 słów kluczowych**: Najbardziej różnicujące słowa między suspicious a legitimate
- **Skalowanie prawdopodobieństw**: 
  - Najlepsze słowo = 100% prawdopodobieństwo
  - Każde kolejne słowo = coraz mniejsze prawdopodobieństwo
  - Im więcej słów kluczowych, tym wyższe prawdopodobieństwo (średnia arytmetyczna)

### 2. Inteligentne Progi Numeryczne
- **Wiek aplikacji**: Im dalej od progu, tym wyższe prawdopodobieństwo
- **Liczba pobrań**: Im mniej pobrań od progu, tym wyższe prawdopodobieństwo
- **Wartości powyżej progu**: Zerowe prawdopodobieństwo

### 3. Obsługa Brakujących Danych
- **Reguła 50%**: Jeśli brakuje informacji, przypisuje 50% prawdopodobieństwo
- **Aplikacje iOS**: Sprawdza nazwę aplikacji dla słów kluczowych
- **Brak jakichkolwiek danych**: 50% dla każdej cechy

### 4. Ważenie Cech
```python
base_weights = {
    'app_keyword': 0.5,    # Słowa w nazwie aplikacji
    'domain_keyword': 0.2,  # Słowa w domenie dewelopera
    'age': 0.15,           # Wiek aplikacji
    'downloads': 0.15      # Liczba pobrań
}
```

## 📊 Przykład Działania

### Przykład 1: Aplikacja z wieloma słowami kluczowymi
```python
app_id = "com.prank.sound.fart.funny"
# Słowa kluczowe: "prank" (100%), "fart" (85%), "funny" (70%)
# Średnia: (100% + 85% + 70%) / 3 = 85%
# Domena dewelopera: brakujące dane, prawdopodobieństwo 50%
# liczba pobrań: brakujące dane, prawdopodobieństwo 50%
# wiek: brakujące dane, prawdopodobieństwo 50%
# Finalne prawdopodobieństwo: 85% * 0.5 + 50% * 0.2 + 50% * 0.15 + 50% * 0.15 = 67.5%
```

### Przykład 2: Aplikacja z brakiem danych
```python
app_id = "123456789"  # iOS app bez danych
# Wszystkie cechy: 50% prawdopodobieństwo
# Finalne prawdopodobieństwo: 50% * (0.5 + 0.2 + 0.15 + 0.15) = 50%
```

## 🛠️ Wymagania Techniczne

### Zależności
```
pandas>=1.5.0
numpy>=1.21.0
scikit-learn>=1.1.0
google-play-scraper>=1.2.0
itunes-app-scraper-dmi>=0.9.6
thefuzz>=0.19.0
matplotlib>=3.5.0
seaborn>=0.11.0
tqdm>=4.64.0
```

### Struktura Plików
```
EmAI/
├── enrich_data.py                    # Wzbogacanie danych
├── build_rules.py                    # Budowanie reguł
├── audit_sample.py                   # Audyt próbki
├── analyze_threshold_impact.py       # Analiza wpływu progów
├── advanced_rules.json               # Wygenerowane reguły
├── enriched_dataset.csv              # Wzbogacone dane
├── audit_results-53755.csv           # Wyniki audytu
├── training_dataset.csv              # Dane treningowe
├── 53755.csv                         # Próbka do audytu
├── README.md                         # Dokumentacja
├── requirements.txt                  # Zależności
└── venv/                            # Środowisko wirtualne
```

## 🔄 Workflow Użycia

### 1. Przygotowanie Środowiska
```bash
# Utwórz środowisko wirtualne
python -m venv venv

# Aktywuj środowisko
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt
```

### 2. Wzbogacanie Danych Treningowych
```bash
python enrich_data.py
```

### 3. Budowanie Reguł Scoringu
```bash
python build_rules.py
```

### 4. Audyt Nowej Próbki
```bash
python audit_sample.py
```

### 5. Analiza Wpływu na Metryki Biznesowe
```bash
python analyze_threshold_impact.py
```

## 🎯 Zastosowania

### Główne Użycia
1. **Filtrowanie Inwentarza**: Automatyczne oznaczanie podejrzanych aplikacji
2. **Kontrola Jakości**: Weryfikacja nowych aplikacji przed zatwierdzeniem
3. **Analiza Trendów**: Identyfikacja wzorców w podejrzanych aplikacjach
4. **Optymalizacja Kampanii**: Unikanie niskiej jakości ruchu reklamowego
5. **Analiza ROI**: Ocena wpływu filtrowania na metryki kampanii

### Integracja
- **API Endpoint**: Możliwość integracji z systemami reklamowymi
- **Batch Processing**: Przetwarzanie dużych zbiorów aplikacji
- **Real-time Scoring**: Natychmiastowa klasyfikacja nowych aplikacji

## 📈 Kluczowe Innowacje

### 1. Zaawansowane Ważenie Słów Kluczowych
- **40 słów kluczowych** zamiast prostego binarnego dopasowania
- **Skalowanie TF-IDF** do prawdopodobieństw
- **Średnia arytmetyczna** dla wielu słów kluczowych

### 2. Inteligentna Obsługa Brakujących Danych
- **Reguła 50%** dla brakujących informacji
- **Specjalna obsługa aplikacji iOS**
- **Ważenie cech** zamiast prostego sumowania

### 3. Dynamiczne Progi
- **Automatyczne znajdowanie** optymalnych progów
- **Skalowanie odległości** od progów
- **Zerowe prawdopodobieństwo** powyżej progów

### 4. Analiza Wpływu Biznesowego
- **Metryki CTR** i konwersji
- **Optymalizacja progów** dla maksymalnego ROI
- **Szczegółowe raportowanie** dla różnych scenariuszy

## 🔮 Rozwój Przyszłości

### Planowane Ulepszenia
1. **Głębokie Uczenie**: Implementacja modeli CNN/RNN
2. **Więcej Źródeł Danych**: Integracja z dodatkowymi API
3. **Real-time Learning**: Adaptacyjne uczenie się nowych wzorców
4. **Dashboard**: Interfejs webowy do monitorowania
5. **Alerty**: System powiadomień o nowych zagrożeniach
6. **A/B Testing**: Automatyczne testowanie różnych progów
7. **Inegracja z modelem LLM**: podłączenie np. specjalnie fine-tuningowanego gpt-4o-mini

## 📝 Licencja

Projekt opracowany przez Emę. Wszystkie prawa zastrzeżone.

---

**Wersja**: 3.0 (4-Modułowa Architektura)  
**Data**: 6.08.2025  
**Autor**: Ema