import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
from thefuzz import fuzz
import warnings
import urllib

warnings.filterwarnings('ignore')

def get_ranked_keywords(df: pd.DataFrame, top_n=200):
    """
    Analizuje app_id i domeny, a następnie zwraca uszeregowaną listę
    słów kluczowych, które najlepiej różnicują klasy.
    """
    print("Analizowanie i ranking słów kluczowych za pomocą TF-IDF...")
    
    stop_words = {'ads', 'txt', 'co', 'com', 'app'}
    
    # --- Słowa kluczowe w nazwie aplikacji ---
    suspicious_corpus_app = " ".join([word for app_id in df[df['label'] == 'suspicious']['app_id'].dropna() if not str(app_id).isdigit() for word in re.findall(r'[a-z]+', str(app_id).lower()) if len(word) > 2 and word not in stop_words])
    legitimate_corpus_app = " ".join([word for app_id in df[df['label'] == 'legitimate']['app_id'].dropna() if not str(app_id).isdigit() for word in re.findall(r'[a-z]+', str(app_id).lower()) if len(word) > 2 and word not in stop_words])

    vectorizer_app = TfidfVectorizer()
    tfidf_matrix_app = vectorizer_app.fit_transform([suspicious_corpus_app, legitimate_corpus_app])
    scores_app = pd.DataFrame({
        'word': vectorizer_app.get_feature_names_out(),
        'tfidf_score': tfidf_matrix_app[0].toarray().flatten()
    }).sort_values(by='tfidf_score', ascending=False)
    
    # --- Słowa kluczowe w domenie dewelopera ---
    suspicious_corpus_domain = " ".join(df[df['label'] == 'suspicious']['developerWebsite'].dropna().apply(lambda url: " ".join([word for word in re.findall(r'[a-z]+', urllib.parse.urlparse(str(url)).netloc) if word not in stop_words])))
    legitimate_corpus_domain = " ".join(df[df['label'] == 'legitimate']['developerWebsite'].dropna().apply(lambda url: " ".join([word for word in re.findall(r'[a-z]+', urllib.parse.urlparse(str(url)).netloc) if word not in stop_words])))

    vectorizer_domain = TfidfVectorizer()
    tfidf_matrix_domain = vectorizer_domain.fit_transform([suspicious_corpus_domain, legitimate_corpus_domain])
    scores_domain = pd.DataFrame({
        'word': vectorizer_domain.get_feature_names_out(),
        'tfidf_score': tfidf_matrix_domain[0].toarray().flatten()
    }).sort_values(by='tfidf_score', ascending=False)

    return scores_app.head(top_n), scores_domain.head(top_n)

def create_features_for_cutoff(df, app_keywords, domain_keywords):
    """Tworzy cechy na podstawie dostarczonych list słów kluczowych."""
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
            
    return features

def main():
    try:
        df_full = pd.read_csv('scored_app_dataset.csv')
        df = df_full[df_full['label'].isin(['suspicious', 'legitimate'])].copy()
    except FileNotFoundError:
        print("BŁĄD: Nie znaleziono pliku 'scored_app_dataset.csv'.")
        return

    ranked_app_keywords, ranked_domain_keywords = get_ranked_keywords(df)
    
    cutoffs = [10, 20, 30, 40, 50, 75, 100, 125, 150]
    performance_results = []

    print("\nRozpoczynanie testowania różnych punktów odcięcia dla liczby słów kluczowych...")
    for n_keywords in cutoffs:
        print(f"  > Testowanie z {n_keywords} najlepszymi słowami kluczowymi...")
        
        app_kw_subset = ranked_app_keywords['word'].head(n_keywords).tolist()
        domain_kw_subset = ranked_domain_keywords['word'].head(n_keywords).tolist()
        
        X = create_features_for_cutoff(df, app_kw_subset, domain_kw_subset)
        y = df['label'].apply(lambda x: 1 if x == 'suspicious' else 0)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
        model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', scale_pos_weight=scale_pos_weight)
        model.fit(X_train, y_train)
        
        y_prob = model.predict_proba(X_test)[:, 1]
        auc_score = roc_auc_score(y_test, y_prob)
        
        performance_results.append({'n_keywords': n_keywords, 'auc': auc_score})

    # --- Analiza wyników ---
    results_df = pd.DataFrame(performance_results)
    best_result = results_df.loc[results_df['auc'].idxmax()]
    optimal_n_keywords = int(best_result['n_keywords'])
    
    print("\n" + "="*60)
    print("  WYNIKI OPTYMALIZACJI LICZBY SŁÓW KLUCZOWYCH")
    print("="*60)
    print("\nSkuteczność modelu (AUC) w zależności od liczby słów kluczowych:")
    print(results_df)

    # Wizualizacja wyników
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=results_df, x='n_keywords', y='auc', marker='o')
    plt.axvline(x=optimal_n_keywords, color='red', linestyle='--', label=f'Optymalny punkt ({optimal_n_keywords} słów)')
    plt.title('Wpływ liczby słów kluczowych na skuteczność modelu (AUC)')
    plt.xlabel('Liczba najlepszych słów kluczowych')
    plt.ylabel('Wynik AUC na zbiorze testowym')
    plt.grid(True)
    plt.legend()
    plt.show()

    print("\n--- REKOMENDACJA ---")
    print(f"Najlepsze wyniki osiągnięto dla {optimal_n_keywords} słów kluczowych (AUC = {best_result['auc']:.4f}).")
    
    print("\nNajważniejsze słowa kluczowe w nazwie aplikacji:")
    print(", ".join(ranked_app_keywords['word'].head(optimal_n_keywords).tolist()))
    
    print("\nNajważniejsze słowa kluczowe w domenie dewelopera:")
    print(", ".join(ranked_domain_keywords['word'].head(optimal_n_keywords).tolist()))

if __name__ == "__main__":
    main()