import pandas as pd
import numpy as np
import re
import json
import urllib.parse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

# Ta funkcja pozostaje z poprzednich skryptów do znalezienia optymalnego progu
def find_optimal_threshold(df, column_name):
    df_filtered = df.dropna(subset=[column_name])
    suspicious_values = df_filtered[df_filtered['label'] == 'suspicious'][column_name]
    legitimate_values = df_filtered[df_filtered['label'] == 'legitimate'][column_name]
    if len(suspicious_values) < 5 or len(legitimate_values) < 5: return None
    search_min = min(suspicious_values.min(), legitimate_values.min())
    search_max = max(suspicious_values.max(), legitimate_values.max())
    best_f1, best_threshold = 0, None
    for threshold in np.linspace(search_min, search_max, 100):
        tp = (suspicious_values <= threshold).sum()
        fp = (legitimate_values <= threshold).sum()
        fn = (suspicious_values > threshold).sum()
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        if f1 > best_f1:
            best_f1, best_threshold = f1, threshold
    return best_threshold

def main():
    print("Rozpoczynam budowanie zaawansowanych reguł...")
    try:
        df = pd.read_csv('scored_app_dataset.csv')
        df_filtered = df[df['label'].isin(['suspicious', 'legitimate'])].copy()
    except FileNotFoundError:
        print("BŁĄD: Nie znaleziono pliku 'scored_app_dataset.csv'.")
        return

    # --- 1. Słowa kluczowe (App ID i Domena) ---
    print(" > Krok 1: Znajdowanie i ważenie 40 najlepszych słów kluczowych...")
    
    # *** ZMIANA: Dodano 'game' do listy ignorowanych słów ***
    stop_words = {'ads', 'txt', 'co', 'com', 'app', 'game'}
    
    # App ID
    suspicious_corpus_app = " ".join([word for app_id in df_filtered[df_filtered['label'] == 'suspicious']['app_id'].dropna() if not str(app_id).isdigit() for word in re.findall(r'[a-z]+', str(app_id).lower()) if len(word) > 2 and word not in stop_words])
    legitimate_corpus_app = " ".join([word for app_id in df_filtered[df_filtered['label'] == 'legitimate']['app_id'].dropna() if not str(app_id).isdigit() for word in re.findall(r'[a-z]+', str(app_id).lower()) if len(word) > 2 and word not in stop_words])
    vectorizer_app = TfidfVectorizer()
    tfidf_matrix_app = vectorizer_app.fit_transform([suspicious_corpus_app, legitimate_corpus_app])
    scores_app_df = pd.DataFrame({'word': vectorizer_app.get_feature_names_out(), 'tfidf_score': tfidf_matrix_app[0].toarray().flatten()}).sort_values(by='tfidf_score', ascending=False).head(40)
    
    # Domena
    suspicious_corpus_domain = " ".join(df_filtered[df_filtered['label'] == 'suspicious']['developerWebsite'].dropna().apply(lambda url: " ".join([word for word in re.findall(r'[a-z]+', urllib.parse.urlparse(str(url)).netloc) if word not in stop_words])))
    legitimate_corpus_domain = " ".join(df_filtered[df_filtered['label'] == 'legitimate']['developerWebsite'].dropna().apply(lambda url: " ".join([word for word in re.findall(r'[a-z]+', urllib.parse.urlparse(str(url)).netloc) if word not in stop_words])))
    vectorizer_domain = TfidfVectorizer()
    tfidf_matrix_domain = vectorizer_domain.fit_transform([suspicious_corpus_domain, legitimate_corpus_domain])
    scores_domain_df = pd.DataFrame({'word': vectorizer_domain.get_feature_names_out(), 'tfidf_score': tfidf_matrix_domain[0].toarray().flatten()}).sort_values(by='tfidf_score', ascending=False).head(40)

    # Skalowanie wyników TF-IDF do zakresu 0-1 (najlepsze słowo ma wagę 1.0)
    scaler = MinMaxScaler()
    scores_app_df['probability'] = scaler.fit_transform(scores_app_df[['tfidf_score']]).flatten()
    scores_domain_df['probability'] = scaler.fit_transform(scores_domain_df[['tfidf_score']]).flatten()

    app_keywords_weighted = dict(zip(scores_app_df['word'], scores_app_df['probability']))
    domain_keywords_weighted = dict(zip(scores_domain_df['word'], scores_domain_df['probability']))

    # --- 2. Progi dla Wieku i Pobrań ---
    print(" > Krok 2: Znajdowanie optymalnych progów dla wieku i pobrań...")
    age_threshold = find_optimal_threshold(df_filtered, 'age_days')
    download_threshold = find_optimal_threshold(df_filtered, 'installs_numeric')

    # --- 3. Zapisanie reguł do pliku JSON ---
    rules = {
        'app_keywords': app_keywords_weighted,
        'domain_keywords': domain_keywords_weighted,
        'age_threshold': age_threshold,
        'download_threshold': download_threshold
    }

    with open('advanced_rules.json', 'w', encoding='utf-8') as f:
        json.dump(rules, f, indent=2, ensure_ascii=False)
        
    print("\nGotowe! Zaawansowane reguły zostały zapisane w pliku 'advanced_rules.json'")

if __name__ == "__main__":
    main()