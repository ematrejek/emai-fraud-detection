import pandas as pd
import numpy as np
import json
import re
from thefuzz import fuzz
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import xgboost as xgb
import warnings

warnings.filterwarnings('ignore', category=UserWarning)

def create_features(df, patterns_path='discovered_patterns.json'):
    """
    Przekształca surowe dane w tabelę cech (features) dla modelu ML.
    """
    try:
        with open(patterns_path, 'r', encoding='utf-8') as f:
            patterns = json.load(f)
        suspicious_keywords = patterns.get('suspicious_keywords', [])
        suspicious_domain_keywords = patterns.get('suspicious_domain_keywords', [])
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku z wzorcami: {patterns_path}")
        return None, None

    features = pd.DataFrame(index=df.index)
    
    for keyword in suspicious_keywords:
        features[f'kw_{keyword}'] = df['app_id'].apply(
            lambda x: 1 if pd.notna(x) and fuzz.partial_ratio(keyword, str(x)) > 90 else 0
        )
    for keyword in suspicious_domain_keywords:
        features[f'domain_kw_{keyword}'] = df['developerWebsite'].apply(
            lambda x: 1 if pd.notna(x) and fuzz.partial_ratio(keyword, str(x)) > 90 else 0
        )

    features['age_days'] = df['age_days']
    features['installs_numeric'] = df['installs_numeric']
    
    for col in ['age_days', 'installs_numeric']:
        if features[col].isnull().any():
            median_val = features[col].median()
            features[col] = features[col].fillna(median_val)
            
    target = df['label'].apply(lambda x: 1 if x == 'suspicious' else 0)
    
    return features, target

def main():
    """Główna funkcja do trenowania i oceny modelu ML dla różnych progów."""
    
    try:
        df = pd.read_csv('scored_app_dataset.csv') # Używamy tego pliku, bo ma już policzony wiek i pobrania
    except FileNotFoundError:
        print("BŁĄD: Nie znaleziono pliku 'scored_app_dataset.csv'.")
        return

    X, y = create_features(df)
    if X is None: return

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Trenowanie modelu XGBoost...")
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', scale_pos_weight=scale_pos_weight)
    model.fit(X_train, y_train)

    # Zdobądź przewidywane prawdopodobieństwa dla klasy 'Suspicious'
    y_prob = model.predict_proba(X_test)[:, 1]

    # --- Analiza dla różnych progów ---
    thresholds_to_check = [0.25, 0.3, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8, 0.9]

    for threshold in thresholds_to_check:
        print("\n" + "="*60)
        print(f"  METRYKI DLA PROGU PRAWDOPODOBIEŃSTWA >= {threshold:.2f}")
        print("="*60)

        y_pred = (y_prob >= threshold).astype(int)

        print("\n--- Raport Klasyfikacji ---\n")
        print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Suspicious']))
        
        print("--- Macierz Pomyłek ---\n")
        cm = confusion_matrix(y_test, y_pred)
        print(pd.DataFrame(cm, 
                         index=['Faktycznie Legitimate', 'Faktycznie Suspicious'], 
                         columns=['Przewidziano Legitimate', 'Przewidziano Suspicious']))
        print("\n")

if __name__ == "__main__":
    main()