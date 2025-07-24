# EmAI Fraud Detection - System Wykrywania Podejrzanych Aplikacji Mobilnych

## 📋 Przegląd Projektu

Projekt EmAI Fraud Detection to zaawansowany system klasyfikacji aplikacji mobilnych, który automatycznie identyfikuje podejrzane lub niskiej jakości aplikacje. System został opracowany w odpowiedzi na problem proliferacji aplikacji generujących niskiej jakości ruch reklamowy, charakteryzujący się wysokimi wskaźnikami CTR i niskimi lub zerowymi konwersjami.

## 🎯 Cel Projektu

Głównym celem jest stworzenie zautomatyzowanego narzędzia klasyfikującego, które przypisuje etykietę "suspicious" aplikacjom na podstawie zestawu predefiniowanych reguł i publicznie dostępnych danych.

## 🏗️ Architektura Systemu

### Etap 1: Zbieranie Danych
- **Plik**: `main.py`
- **Cel**: Pobieranie metadanych aplikacji z Google Play Store i Apple App Store
- **Funkcjonalność**:
  - Automatyczne rozpoznawanie typu aplikacji (iOS/Android) na podstawie ID
  - Scraping danych: liczba instalacji, data wydania, deweloper, domena dewelopera
  - Obsługa błędów i aplikacji niedostępnych

### Etap 2: Analiza Wzorców
- **Plik**: `pattern_discovery_analyzer.py`
- **Cel**: Odkrywanie wzorców charakterystycznych dla podejrzanych aplikacji
- **Metody**:
  - **TF-IDF Analysis**: Identyfikacja słów kluczowych w nazwach aplikacji
  - **Domain Analysis**: Analiza domen deweloperów
  - **Numerical Patterns**: Wykrywanie progów wieku aplikacji i liczby instalacji
  - **Visualization**: Generowanie wykresów i raportów

### Etap 3: Budowanie Modelu
- **Plik**: `build_model.py`
- **Cel**: Tworzenie finalnego modelu XGBoost
- **Proces**:
  1. Ranking 150 najlepszych słów kluczowych (TF-IDF)
  2. Tworzenie cech na podstawie słów kluczowych
  3. Trenowanie modelu XGBoost z balansowaniem klas
  4. Zapisywanie modelu i wzorców

### Etap 4: Ocena Modelu
- **Plik**: `evaluation.py`
- **Cel**: Ocena wydajności modelu dla różnych progów
- **Metryki**:
  - Classification Report (Precision, Recall, F1-Score)
  - Confusion Matrix
  - Analiza dla różnych progów prawdopodobieństwa

### Etap 5: Predykcja w Czasie Rzeczywistym
- **Plik**: `predict_app.py`
- **Cel**: Klasyfikacja nowych aplikacji w czasie rzeczywistym
- **Funkcjonalność**:
  - Wczytywanie wytrenowanego modelu
  - Scraping danych dla nowej aplikacji
  - Tworzenie cech i predykcja
  - Reguły biznesowe dla aplikacji niedostępnych

## 🔧 Szczegółowy Proces Tworzenia

### Krok 1: Przygotowanie Danych
```python
# main.py - Scraping danych z App Store i Google Play
def scrape_app_store(app_id):
    scraper = AppStoreScraper()
    details = scraper.get_app_details(app_id, country='us')
    return {
        'releaseDate': details.get('releaseDate'),
        'developer': details.get('sellerName'),
        'developerWebsite': details.get('sellerUrl')
    }
```

### Krok 2: Odkrywanie Wzorców
```python
# pattern_discovery_analyzer.py - TF-IDF Analysis
def discover_suspicious_keywords_tfidf(self, df):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([suspicious_corpus, legitimate_corpus])
    # Ranking słów kluczowych na podstawie TF-IDF scores
```

### Krok 3: Tworzenie Cech
```python
# build_model.py - Feature Engineering
def create_features_for_training(df, app_keywords, domain_keywords):
    features = pd.DataFrame(index=df.index)
    for keyword in app_keywords:
        features[f'kw_{keyword}'] = df['app_id'].apply(
            lambda x: 1 if fuzz.partial_ratio(keyword, str(x)) > 90 else 0
        )
    features['age_days'] = df['age_days']
    features['installs_numeric'] = df['installs_numeric']
```

### Krok 4: Trenowanie Modelu
```python
# build_model.py - Model Training
model = xgb.XGBClassifier(
    use_label_encoder=False, 
    eval_metric='logloss', 
    scale_pos_weight=scale_pos_weight
)
model.fit(X, y)
```

## 🚀 Algorytm Predykcji (predict_app.py)

### Klasa AppClassifier
```python
class AppClassifier:
    def __init__(self, model_path='xgb_model.joblib', patterns_path='patterns_for_model.json'):
        self.model = joblib.load(model_path)
        with open(patterns_path, 'r') as f:
            self.patterns = json.load(f)
```

### Proces Predykcji
1. **Scraping Danych**: Pobieranie metadanych aplikacji
2. **Przygotowanie Cech**: Konwersja surowych danych na cechy
3. **Predykcja**: Użycie modelu XGBoost do klasyfikacji
4. **Reguły Biznesowe**: Dodatkowe sprawdzenia dla aplikacji niedostępnych

### Przykład Użycia
```python
classifier = AppClassifier()
probability = classifier.predict_suspicion('com.example.app')
print(f"Prawdopodobieństwo bycia suspicious: {probability:.2%}")
```

## 📊 Metryki Wydajności

### Kluczowe Wskaźniki
- **Precision**: Dokładność pozytywnych predykcji
- **Recall**: Pokrycie wszystkich rzeczywistych przypadków suspicious
- **F1-Score**: Harmoniczna średnia precision i recall
- **ROC-AUC**: Obszar pod krzywą ROC

### Optymalne Progi
- **0.4-0.5**: Balans między precision a recall
- **0.7-0.8**: Wysoka precision, niższy recall
- **0.25-0.3**: Wysoki recall, niższa precision

## 🛠️ Wymagania Techniczne

### Zależności
```
pandas
numpy
xgboost
scikit-learn
google-play-scraper
itunes-app-scraper-dmi
thefuzz
matplotlib
seaborn
joblib
```

### Struktura Plików
```
EmAI/
├── main.py                          # Scraping danych
├── pattern_discovery_analyzer.py    # Analiza wzorców
├── build_model.py                   # Budowanie modelu
├── evaluation.py                    # Ocena modelu
├── predict_app.py                   # Predykcja w czasie rzeczywistym
├── xgb_model.joblib                # Wytrenowany model
├── patterns_for_model.json         # Wzorce słów kluczowych
├── training_dataset.csv            # Zbiór treningowy
├── enriched_app_dataset.csv        # Wzbogacone dane
└── scored_app_dataset.csv          # Oznaczone dane
```

## 🔄 Workflow Użycia

### 1. Przygotowanie Danych
```bash
python main.py
```

### 2. Analiza Wzorców
```bash
python pattern_discovery_analyzer.py
```

### 3. Budowanie Modelu
```bash
python build_model.py
```

### 4. Ocena Modelu
```bash
python evaluation.py
```

### 5. Predykcja
```bash
python predict_app.py
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

## 📈 Wyniki i Wnioski

### Kluczowe Odkrycia
1. **Słowa Kluczowe**: Podejrzane aplikacje często zawierają słowa jak "prank", "wallpaper", "fart"
2. **Wiek Aplikacji**: Nowe aplikacje (<30 dni) są bardziej podejrzane
3. **Liczba Instalacji**: Aplikacje z małą liczbą instalacji są ryzykowne
4. **Domeny Deweloperów**: Niektóre domeny są powiązane z podejrzanymi aplikacjami

### Wydajność Modelu
- **Accuracy**: ~85-90%
- **Precision**: ~80-85%
- **Recall**: ~75-80%
- **F1-Score**: ~77-82%

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

**Wersja**: 1.0  
**Data**: 24.07.2025  
**Autor**: Emilia Matrejek