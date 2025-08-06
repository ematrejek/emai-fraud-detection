import pandas as pd
import numpy as np
import re
import json
import urllib.parse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

def find_optimal_threshold(df, column_name):
    """Znajduje optymalny próg separujący dwie grupy na podstawie F1-score."""
    df_filtered = df.dropna(subset=[column_name])
    suspicious_values = df_filtered[df_filtered['label'] == 'suspicious'][column_name]
    legitimate_values = df_filtered[df_filtered['label'] == 'legitimate'][column_name]
    if len(suspicious_values) < 5 or len(legitimate_values) < 5: return None
    search_min = min(suspicious_values.min(), legitimate_values.min())
    search_max = max(suspicious_values.max(), legitimate_values.max())
    best_f1, best_threshold = 0, None
    for threshold in np.linspace(search_min, search_max, 100):
        tp = (suspicious_values <= threshold).sum(); fp = (legitimate_values <= threshold).sum(); fn = (suspicious_values > threshold).sum()
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        if f1 > best_f1: best_f1, best_threshold = f1, threshold
    return best_threshold

def main():
    print("Rozpoczynam budowanie zaawansowanych reguł...")
    try:
        # *** ZMIANA: Poprawiono nazwę pliku wejściowego ***
        df = pd.read_csv('enriched_dataset.csv')
        df_filtered = df[df['label'].isin(['suspicious', 'legitimate'])].copy()
    except (FileNotFoundError, KeyError):
        # *** ZMIANA: Poprawiono komunikat błędu ***
        print("BŁĄD: Nie znaleziono pliku 'enriched_dataset.csv' lub brak w nim kolumny 'label'.")
        print("Upewnij się, że najpierw uruchomiłeś skrypt '1_enrich_data.py'.")
        return

    print(" > Krok 1: Znajdowanie i ważenie 40 najlepszych słów kluczowych...")
    app_stop_words = {'ads', 'txt', 'co', 'com', 'app', 'game'}
    
    def get_text_for_analysis(row):
        return row['appName'] if str(row['app_id']).isdigit() and pd.notna(row['appName']) else row['app_id']
        
    df_filtered['text_for_keywords'] = df_filtered.apply(get_text_for_analysis, axis=1)

    suspicious_corpus_app = " ".join([word for text in df_filtered[df_filtered['label'] == 'suspicious']['text_for_keywords'].dropna() for word in re.findall(r'[a-z]+', str(text).lower()) if len(word) > 2 and word not in app_stop_words])
    legitimate_corpus_app = " ".join([word for text in df_filtered[df_filtered['label'] == 'legitimate']['text_for_keywords'].dropna() for word in re.findall(r'[a-z]+', str(text).lower()) if len(word) > 2 and word not in app_stop_words])

    if not suspicious_corpus_app or not legitimate_corpus_app:
        print("OSTRZEŻENIE: Brak wystarczających danych tekstowych do analizy słów kluczowych w nazwach.")
        app_keywords_weighted = {}
    else:
        vectorizer_app = TfidfVectorizer()
        tfidf_matrix_app = vectorizer_app.fit_transform([suspicious_corpus_app, legitimate_corpus_app])
        scores_app_df = pd.DataFrame({'word': vectorizer_app.get_feature_names_out(), 'tfidf_score': tfidf_matrix_app[0].toarray().flatten()}).sort_values(by='tfidf_score', ascending=False).head(40)
        scaler = MinMaxScaler()
        scores_app_df['probability'] = scaler.fit_transform(scores_app_df[['tfidf_score']]).flatten()
        app_keywords_weighted = dict(zip(scores_app_df['word'], scores_app_df['probability']))

    domain_stop_words = {'www', 'http', 'https', 'io', 'com', 'pl', 'org', 'net', 'gov', 'edu', 'info', 'biz', 'de', 'uk', 'ru', 'fr', 'eu', 'app', 'xyz', 'top', 'site'}
    def extract_clean_domain_words(url):
        if pd.isna(url): return ""
        try:
            domain_text = urllib.parse.urlparse(str(url)).netloc.lower()
            words = re.findall(r'[a-z]+', domain_text)
            clean_words = [word for word in words if word not in domain_stop_words]
            return " ".join(clean_words)
        except: return ""

    suspicious_corpus_domain = " ".join(df_filtered[df_filtered['label'] == 'suspicious']['developerWebsite'].apply(extract_clean_domain_words))
    legitimate_corpus_domain = " ".join(df_filtered[df_filtered['label'] == 'legitimate']['developerWebsite'].apply(extract_clean_domain_words))
    
    if not suspicious_corpus_domain or not legitimate_corpus_domain:
        print("OSTRZEŻENIE: Brak wystarczających danych tekstowych do analizy słów kluczowych w domenach.")
        domain_keywords_weighted = {}
    else:
        vectorizer_domain = TfidfVectorizer()
        tfidf_matrix_domain = vectorizer_domain.fit_transform([suspicious_corpus_domain, legitimate_corpus_domain])
        scores_domain_df = pd.DataFrame({'word': vectorizer_domain.get_feature_names_out(), 'tfidf_score': tfidf_matrix_domain[0].toarray().flatten()}).sort_values(by='tfidf_score', ascending=False).head(40)
        scaler_domain = MinMaxScaler()
        scores_domain_df['probability'] = scaler_domain.fit_transform(scores_domain_df[['tfidf_score']]).flatten()
        domain_keywords_weighted = dict(zip(scores_domain_df['word'], scores_domain_df['probability']))

    print(" > Krok 2: Znajdowanie optymalnych progów dla wieku i pobrań...")
    age_threshold = find_optimal_threshold(df_filtered, 'age_days')
    download_threshold = find_optimal_threshold(df_filtered, 'installs_numeric')

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