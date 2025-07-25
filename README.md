# EmAI Fraud Detection - Zaawansowany System Wykrywania Podejrzanych Aplikacji Mobilnych

## 📋 Przegląd Projektu

Projekt EmAI Fraud Detection to zaawansowany system klasyfikacji aplikacji mobilnych, który automatycznie identyfikuje podejrzane lub niskiej jakości aplikacje. System wykorzystuje **zaawansowane reguły scoringu** oparte na analizie 40 słów kluczowych, progach wieku i pobrań, oraz inteligentnej obsłudze brakujących danych.

## 🎯 Cel Projektu

Głównym celem jest stworzenie zautomatyzowanego narzędzia klasyfikującego, które przypisuje **prawdopodobieństwo bycia suspicious** aplikacjom na podstawie zaawansowanych reguł i publicznie dostępnych danych.

## 🏗️ Nowa Architektura Systemu

### Etap 1: Budowanie Zaawansowanych Reguł
- **Plik**: `build_advanced_rules.py`
- **Cel**: Tworzenie zaawansowanych reguł scoringu na podstawie analizy danych
- **Funkcjonalność**:
  - **40 słów kluczowych**: Ranking i ważenie słów kluczowych w nazwach aplikacji i domenach
  - **TF-IDF Analysis**: Identyfikacja najbardziej różnicujących słów
  - **Skalowanie prawdopodobieństw**: Najlepsze słowo = 100%, każde kolejne coraz mniej
  - **Optymalne progi**: Automatyczne znajdowanie progów dla wieku i pobrań

### Etap 2: Zaawansowany Scorer
- **Plik**: `advanced_scorer.py`
- **Cel**: Klasyfikacja aplikacji w czasie rzeczywistym z zaawansowaną logiką
- **Funkcjonalność**:
  - **Inteligentny scoring**: Im więcej słów kluczowych, tym wyższe prawdopodobieństwo
  - **Obsługa brakujących danych**: 50% prawdopodobieństwo dla brakujących informacji
  - **Ważenie cech**: Różne wagi dla różnych typów cech
  - **Reguły biznesowe**: Specjalne obsługa aplikacji iOS i niedostępnych danych

## 🔧 Szczegółowy Proces Tworzenia

### Krok 1: Budowanie Reguł (`build_advanced_rules.py`)
```python
# Analiza 40 najlepszych słów kluczowych
scores_app_df = pd.DataFrame({
    'word': vectorizer_app.get_feature_names_out(), 
    'tfidf_score': tfidf_matrix_app[0].toarray().flatten()
}).sort_values(by='tfidf_score', ascending=False).head(40)

# Skalowanie do zakresu 0-1 (najlepsze słowo = 100%)
scaler = MinMaxScaler()
scores_app_df['probability'] = scaler.fit_transform(scores_app_df[['tfidf_score']]).flatten()
```

### Krok 2: Zaawansowany Scoring (`advanced_scorer.py`)
```python
class AdvancedRuleScorer:
    def __init__(self, rules_path='advanced_rules.json'):
        self.base_weights = {
            'app_keyword': 0.5,    # 50% waga dla słów w nazwie
            'domain_keyword': 0.2,  # 20% waga dla słów w domenie
            'age': 0.15,           # 15% waga dla wieku
            'downloads': 0.15      # 15% waga dla pobrań
        }
```

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
# Finalne prawdopodobieństwo: 85% * 0.5 = 42.5%
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
```

### Struktura Plików
```
EmAI/
├── build_advanced_rules.py      # Budowanie reguł
├── advanced_scorer.py           # Zaawansowany scorer
├── main.py                      # Scraping danych
├── pattern_discovery_analyzer.py # Analiza wzorców
├── evaluation.py                # Ocena modelu
├── advanced_rules.json          # Wygenerowane reguły
├── README.md                    # Dokumentacja
├── requirements.txt             # Zależności
├── deploy.sh                    # Skrypt instalacji (Linux/Mac)
└── deploy.bat                   # Skrypt instalacji (Windows)
```

## 🔄 Workflow Użycia

### 1. Przygotowanie Danych
```bash
python main.py
```

### 2. Budowanie Zaawansowanych Reguł
```bash
python build_advanced_rules.py
```

### 3. Predykcja z Zaawansowanym Scorerem
```bash
python advanced_scorer.py
```

### 4. Ocena Modelu
```bash
python evaluation.py
```

## 🎯 Zastosowania

### Główne Użycia
1. **Filtrowanie Inwentarza**: Automatyczne oznaczanie podejrzanych aplikacji
2. **Kontrola Jakości**: Weryfikacja nowych aplikacji przed zatwierdzeniem
3. **Analiza Trendów**: Identyfikacja wzorców w podejrzanych aplikacjach
4. **Optymalizacja Kampanii**: Unikanie niskiej jakości ruchu reklamowego

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

## 🔮 Rozwój Przyszłości

### Planowane Ulepszenia
1. **Głębokie Uczenie**: Implementacja modeli CNN/RNN
2. **Więcej Źródeł Danych**: Integracja z dodatkowymi API
3. **Real-time Learning**: Adaptacyjne uczenie się nowych wzorców
4. **Dashboard**: Interfejs webowy do monitorowania
5. **Alerty**: System powiadomień o nowych zagrożeniach

## 📝 Licencja

Projekt opracowany przez Emę. Wszystkie prawa zastrzeżone.

---

**Wersja**: 2.0 (Zaawansowane Reguły)  
**Data**: 24.07.2025  
**Autor**: Emilia Matrejek