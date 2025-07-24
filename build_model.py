import pandas as pd
import numpy as np
import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer
import xgboost as xgb
import joblib
import urllib.parse
from thefuzz import fuzz
import warnings
warnings.filterwarnings('ignore')

def get_ranked_keywords(df: pd.DataFrame, top_n=150):
    """Zwraca uszeregowaną listę 150 najlepszych słów kluczowych."""
    print("1. Analizowanie i ranking 150 najlepszych słów kluczowych...")
    stop_words = {'ads', 'txt', 'co', 'com', 'app'}
    
    # Słowa kluczowe w nazwie aplikacji
    suspicious_corpus_app = " ".join([word for app_id in df[df['label'] == 'suspicious']['app_id'].dropna() if not str(app_id).isdigit() for word in re.findall(r'[a-z]+', str(app_id).lower()) if len(word) > 2 and word not in stop_words])
    legitimate_corpus_app = " ".join([word for app_id in df[df['label'] == 'legitimate']['app_id'].dropna() if not str(app_id).isdigit() for word in re.findall(r'[a-z]+', str(app_id).lower()) if len(word) > 2 and word not in stop_words])
    vectorizer_app = TfidfVectorizer()
    tfidf_matrix_app = vectorizer_app.fit_transform([suspicious_corpus_app, legitimate_corpus_app])
    scores_app = pd.DataFrame({'word': vectorizer_app.get_feature_names_out(), 'tfidf_score': tfidf_matrix_app[0].toarray().flatten()}).sort_values(by='tfidf_score', ascending=False)
    
    # Słowa kluczowe w domenie dewelopera
    suspicious_corpus_domain = " ".join(df[df['label'] == 'suspicious']['developerWebsite'].dropna().apply(lambda url: " ".join([word for word in re.findall(r'[a-z]+', urllib.parse.urlparse(str(url)).netloc) if word not in stop_words])))
    legitimate_corpus_domain = " ".join(df[df['label'] == 'legitimate']['developerWebsite'].dropna().apply(lambda url: " ".join([word for word in re.findall(r'[a-z]+', urllib.parse.urlparse(str(url)).netloc) if word not in stop_words])))
    vectorizer_domain = TfidfVectorizer()
    tfidf_matrix_domain = vectorizer_domain.fit_transform([suspicious_corpus_domain, legitimate_corpus_domain])
    scores_domain = pd.DataFrame({'word': vectorizer_domain.get_feature_names_out(), 'tfidf_score': tfidf_matrix_domain[0].toarray().flatten()}).sort_values(by='tfidf_score', ascending=False)

    return scores_app.head(top_n)['word'].tolist(), scores_domain.head(top_n)['word'].tolist()

def create_features_for_training(df, app_keywords, domain_keywords):
    """Tworzy cechy dla modelu na podstawie zoptymalizowanych słów kluczowych."""
    print("2. Tworzenie cech na podstawie 150 najlepszych słów kluczowych...")
    features = pd.DataFrame(index=df.index)
    for keyword in app_keywords:
        features[f'kw_{keyword}'] = df['app_id'].apply(lambda x: 1 if pd.notna(x) and fuzz.partial_ratio(keyword, str(x)) > 90 else 0)
    for keyword in domain_keywords:
        features[f'domain_kw_{keyword}'] = df['developerWebsite'].apply(lambda x: 1 if pd.notna(x) and fuzz.partial_ratio(keyword, str(x)) > 90 else 0)
    
    features['age_days'] = df['age_days']
    features['installs_numeric'] = df['installs_numeric']

    for col in ['age_days', 'installs_numeric']:
        if features[col].isnull().any():
            features[col] = features[col].fillna(features[col].median())
            
    target = df['label'].apply(lambda x: 1 if x == 'suspicious' else 0)
    return features, target

def main():
    try:
        df = pd.read_csv('scored_app_dataset.csv')
        df_filtered = df[df['label'].isin(['suspicious', 'legitimate'])].copy()
    except FileNotFoundError:
        print("BŁĄD: Nie znaleziono pliku 'scored_app_dataset.csv'.")
        return

    # Krok 1: Odkryj optymalne słowa kluczowe
    app_keywords, domain_keywords = get_ranked_keywords(df_filtered, top_n=150)
    
    # Zapisz wzorce do pliku
    patterns = {'suspicious_keywords': app_keywords, 'suspicious_domain_keywords': domain_keywords}
    with open('patterns_for_model.json', 'w', encoding='utf-8') as f:
        json.dump(patterns, f, indent=2, ensure_ascii=False)
    print("Zapisano 150 najlepszych słów kluczowych do 'patterns_for_model.json'")

    # Krok 2: Stwórz cechy i wytrenuj finalny model
    X, y = create_features_for_training(df_filtered, app_keywords, domain_keywords)
    
    print("3. Trenowanie finalnego modelu XGBoost na pełnym zbiorze danych...")
    scale_pos_weight = (y == 0).sum() / (y == 1).sum()
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', scale_pos_weight=scale_pos_weight)
    model.fit(X, y)

    # Krok 3: Zapisz wytrenowany model
    joblib.dump(model, 'xgb_model.joblib')
    print("\nFinalny model został pomyślnie wytrenowany i zapisany jako 'xgb_model.joblib'!")

if __name__ == "__main__":
    main()