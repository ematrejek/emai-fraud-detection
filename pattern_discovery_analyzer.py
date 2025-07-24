import pandas as pd
import numpy as np
import re
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import urllib.parse
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
import json

warnings.filterwarnings('ignore')

class PatternDiscoveryAnalyzer:
    def __init__(self):
        self.suspicious_keywords = []
        self.suspicious_domains = []
        self.download_threshold = None
        self.age_threshold = None
        
    def load_data(self, file_path):
        """Ładuje dane z pliku CSV"""
        try:
            df = pd.read_csv(file_path)
            df['installs_numeric'] = df['installs'].apply(lambda x: re.sub(r'[^\d]', '', str(x)) if pd.notna(x) else '')
            df['installs_numeric'] = pd.to_numeric(df['installs_numeric'], errors='coerce')
            
            def to_days(date_str):
                if pd.isna(date_str): return None
                date_formats = ['%b %d, %Y', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
                for fmt in date_formats:
                    try:
                        release_dt = datetime.strptime(str(date_str).strip(), fmt)
                        return (datetime.now() - release_dt).days
                    except (ValueError, TypeError):
                        continue
                return None
            df['age_days'] = df['releaseDate'].apply(to_days)

            print(f"Załadowano {len(df)} aplikacji z pliku {file_path}")
            return df
        except Exception as e:
            print(f"Błąd podczas ładowania danych: {e}")
            return None

    def discover_suspicious_keywords_tfidf(self, df):
        """Odkrywa słowa kluczowe używając TF-IDF, z ręcznym filtrowaniem stop words."""
        print("\n=== ODKRYWANIE SŁÓW KLUCZOWYCH (METODA TF-IDF) ===")
        
        suspicious_df = df[df['label'] == 'suspicious']
        legitimate_df = df[df['label'] == 'legitimate']

        if suspicious_df.empty or legitimate_df.empty:
            print("Brak wystarczających danych do analizy słów kluczowych.")
            return {}
        
        # *** ZMIANA: Używamy zbioru dla szybszego sprawdzania ***
        stop_words = {'ads', 'txt', 'co', 'com', 'app'}

        def get_corpus(app_ids):
            words = []
            for app_id in app_ids:
                if not str(app_id).isdigit():
                    app_name_parts = re.findall(r'[a-z]+', str(app_id).lower())
                    # *** ZMIANA: Ręczne filtrowanie stop words dla pewności ***
                    filtered_words = [word for word in app_name_parts if len(word) > 2 and word not in stop_words]
                    words.extend(filtered_words)
            return " ".join(words)

        corpus = [get_corpus(suspicious_df['app_id']), get_corpus(legitimate_df['app_id'])]
        
        # Usunęliśmy parametr stop_words, bo filtrujemy ręcznie
        vectorizer = TfidfVectorizer()
        
        tfidf_matrix = vectorizer.fit_transform(corpus)
        feature_names = vectorizer.get_feature_names_out()
        
        suspicious_scores = tfidf_matrix[0].toarray().flatten()
        
        tfidf_scores_df = pd.DataFrame({'word': feature_names, 'tfidf_score': suspicious_scores})
        
        legit_corpus = set(corpus[1].split())
        tfidf_scores_df = tfidf_scores_df[~tfidf_scores_df['word'].isin(legit_corpus) | (tfidf_scores_df['tfidf_score'] > 0.1)]
        
        top_keywords_df = tfidf_scores_df.sort_values(by='tfidf_score', ascending=False).head(20)
        
        print("\nTOP 20 PODEJRZANYCH SŁÓW KLUCZOWYCH (TF-IDF):")
        print(top_keywords_df)
        
        self.suspicious_keywords = top_keywords_df['word'].tolist()
        return dict(zip(top_keywords_df['word'], top_keywords_df['tfidf_score']))

    def find_optimal_threshold(self, df, column_name, comparison_type='lower_is_suspicious'):
        """Znajduje optymalny próg separujący dwie grupy na podstawie F1-score."""
        df_filtered = df.dropna(subset=[column_name])
        suspicious_values = df_filtered[df_filtered['label'] == 'suspicious'][column_name]
        legitimate_values = df_filtered[df_filtered['label'] == 'legitimate'][column_name]

        if len(suspicious_values) < 5 or len(legitimate_values) < 5: return None
        
        search_min = min(suspicious_values.min(), legitimate_values.min())
        search_max = max(suspicious_values.max(), legitimate_values.max())
        
        best_f1 = 0
        best_threshold = None
        
        for threshold in np.linspace(search_min, search_max, 100):
            if comparison_type == 'lower_is_suspicious':
                tp = (suspicious_values <= threshold).sum()
                fp = (legitimate_values <= threshold).sum()
                fn = (suspicious_values > threshold).sum()
            else: # higher_is_suspicious
                tp = (suspicious_values >= threshold).sum()
                fp = (legitimate_values >= threshold).sum()
                fn = (suspicious_values < threshold).sum()

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = threshold
        
        return best_threshold
        
    def discover_numerical_patterns(self, df, column_name, pattern_name):
        """Uogólniona funkcja do odkrywania wzorców w danych numerycznych."""
        print(f"\n=== ANALIZA WZORCÓW - {pattern_name.upper()} ===")
        df_filtered = df.dropna(subset=[column_name])
        
        suspicious_data = df_filtered[df_filtered['label'] == 'suspicious'][column_name]
        legitimate_data = df_filtered[df_filtered['label'] == 'legitimate'][column_name]
        
        if len(suspicious_data) < 5 or len(legitimate_data) < 5:
            print(f"Brak wystarczających danych do analizy {pattern_name}.")
            return None

        print(f"\nPorównanie statystyk ({pattern_name}):")
        print(f"  Suspicious - Mediana: {suspicious_data.median():.0f}, Średnia: {suspicious_data.mean():.0f}")
        print(f"  Legitimate - Mediana: {legitimate_data.median():.0f}, Średnia: {legitimate_data.mean():.0f}")
        
        optimal_threshold = self.find_optimal_threshold(df, column_name, 
                                                        comparison_type='lower_is_suspicious')
        
        if optimal_threshold is not None:
            print(f"\nNAJLEPSZY PRÓG ODRÓŻNIAJĄCY: {optimal_threshold:.0f}")
            print(f"(Aplikacje z wartością <= {optimal_threshold:.0f} są bardziej prawdopodobne jako 'suspicious')")
            return int(optimal_threshold)
        else:
            print("\nNie udało się znaleźć jednoznacznego progu odróżniającego.")
            return None

    def discover_domain_patterns(self, df):
        """Odkrywa wzorce w domenach developera, w tym TLD i słowa kluczowe."""
        print("\n=== ANALIZA WZORCÓW DOMEN DEVELOPERA ===")
        df_url = df[df['developerWebsite'].notna()].copy()
        
        # *** ZMIANA: Używamy zbioru dla szybszego sprawdzania ***
        stop_words = {'ads', 'txt', 'co', 'com', 'app'}

        def extract_domain_parts(url):
            try:
                domain = urllib.parse.urlparse(str(url)).netloc.lower().replace('www.', '')
                if not domain: return None, None, None
                parts = domain.split('.')
                tld = parts[-1]
                domain_name = ".".join(parts[:-1])
                domain_keywords_raw = re.findall(r'[a-z]+', domain_name)
                # *** ZMIANA: Ręczne filtrowanie stop words dla pewności ***
                domain_keywords = [word for word in domain_keywords_raw if word not in stop_words]
                return domain, tld, domain_keywords
            except:
                return None, None, None

        df_url[['full_domain', 'tld', 'domain_keywords']] = df_url['developerWebsite'].apply(
            lambda x: pd.Series(extract_domain_parts(x))
        )

        suspicious_tlds = df_url[df_url['label'] == 'suspicious']['tld'].dropna()
        legitimate_tlds = df_url[df_url['label'] == 'legitimate']['tld'].dropna()
        
        if not suspicious_tlds.empty:
            suspicious_tld_counts = Counter(suspicious_tlds)
            legitimate_tld_counts = Counter(legitimate_tlds)
            
            tld_scores = {}
            for tld, count in suspicious_tld_counts.items():
                ratio = count / (legitimate_tld_counts.get(tld, 0) + 1)
                if ratio > 2 and count > 2:
                    tld_scores[tld] = ratio
            
            sorted_tlds = sorted(tld_scores.items(), key=lambda x: x[1], reverse=True)
            print("\nTOP PODEJRZANE KOŃCÓWKI DOMEN (TLD):")
            for tld, ratio in sorted_tlds[:5]:
                print(f"  .{tld} (współczynnik: {ratio:.2f})")

        suspicious_domains_corpus = " ".join([" ".join(kw) for kw in df_url[df_url['label'] == 'suspicious']['domain_keywords'].dropna()])
        legitimate_domains_corpus = " ".join([" ".join(kw) for kw in df_url[df_url['label'] == 'legitimate']['domain_keywords'].dropna()])

        if suspicious_domains_corpus and legitimate_domains_corpus:
            corpus = [suspicious_domains_corpus, legitimate_domains_corpus]
            
            # Usunęliśmy parametr stop_words, bo filtrujemy ręcznie
            vectorizer = TfidfVectorizer()
            
            tfidf_matrix = vectorizer.fit_transform(corpus)
            feature_names = vectorizer.get_feature_names_out()
            suspicious_scores = tfidf_matrix[0].toarray().flatten()

            domain_keywords_df = pd.DataFrame({'word': feature_names, 'tfidf_score': suspicious_scores})
            top_domain_keywords = domain_keywords_df.sort_values(by='tfidf_score', ascending=False).head(10)
            
            print("\nTOP 10 PODEJRZANYCH SŁÓW KLUCZOWYCH W DOMENACH:")
            print(top_domain_keywords)
            self.suspicious_domains = top_domain_keywords['word'].tolist()
        
        return self.suspicious_domains

    def create_visualizations(self, df):
        """Tworzy ulepszone wizualizacje odkrytych wzorców."""
        print("\nTworzę wizualizacje wzorców...")
        sns.set_style("whitegrid")
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Porównanie Aplikacji Suspicious vs. Legitimate', fontsize=16, fontweight='bold')

        ax1 = axes[0]
        if df['installs_numeric'].notna().any():
            sns.kdeplot(data=df, x='installs_numeric', hue='label', fill=True, 
                        ax=ax1, palette={'suspicious': 'red', 'legitimate': 'green'}, log_scale=True)
            ax1.set_title('Gęstość Rozkładu Pobrań (Skala Log)')
            ax1.set_xlabel('Liczba Pobrań')
            if self.download_threshold:
                ax1.axvline(x=self.download_threshold, color='blue', linestyle='--', 
                            label=f'Optymalny Próg ({self.download_threshold:,.0f})')
            ax1.legend()
            
        ax2 = axes[1]
        if df['age_days'].notna().any():
            sns.kdeplot(data=df, x='age_days', hue='label', fill=True, 
                        ax=ax2, palette={'suspicious': 'red', 'legitimate': 'green'})
            ax2.set_title('Gęstość Rozkładu Wieku Aplikacji')
            ax2.set_xlabel('Wiek (dni)')
            if self.age_threshold:
                 ax2.axvline(x=self.age_threshold, color='blue', linestyle='--',
                             label=f'Optymalny Próg ({self.age_threshold:,.0f} dni)')
            ax2.legend()

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig('discovered_patterns.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Wizualizacje zostały zapisane jako 'discovered_patterns.png'")

    def generate_final_report(self):
        """Generuje końcowy raport z odkrytymi wzorcami."""
        print("\n" + "="*80)
        print("KOŃCOWY RAPORT - ODKRYTE WZORCE I REGUŁY")
        print("="*80)
        
        print("\nSugerowane reguły do identyfikacji aplikacji 'suspicious':")
        
        if self.suspicious_keywords:
            print(f"\n1. SŁOWA KLUCZOWE W NAZWIE (Top {len(self.suspicious_keywords)}):")
            print(f"   -> Aplikacja jest podejrzana, jeśli jej nazwa zawiera jedno z słów: {', '.join(self.suspicious_keywords)}")
        
        if self.download_threshold:
             print(f"\n2. PRÓG POBRAŃ:")
             print(f"   -> Aplikacja jest podejrzana, jeśli ma MNIEJ NIŻ lub RÓWNO {self.download_threshold:,.0f} pobrań.")

        if self.age_threshold:
            print(f"\n3. PRÓG WIEKU APLIKACJI:")
            print(f"   -> Aplikacja jest podejrzana, jeśli ma MNIEJ NIŻ lub RÓWNO {self.age_threshold:,.0f} dni.")

        if self.suspicious_domains:
            print(f"\n4. SŁOWA KLUCZOWE W DOMENIE DEWELOPERA (Top {len(self.suspicious_domains)}):")
            print(f"   -> Aplikacja jest podejrzana, jeśli domena jej dewelopera zawiera jedno z słów: {', '.join(self.suspicious_domains)}")
            
        patterns_data = {
            'suspicious_keywords': self.suspicious_keywords,
            'download_threshold': self.download_threshold,
            'age_threshold': self.age_threshold,
            'suspicious_domain_keywords': self.suspicious_domains
        }
        
        with open('discovered_patterns.json', 'w', encoding='utf-8') as f:
            json.dump(patterns_data, f, indent=2, ensure_ascii=False)
        print(f"\nOdkryte wzorce i reguły zostały zapisane w pliku 'discovered_patterns.json'")
        
        return patterns_data

def main():
    """Główna funkcja programu"""
    analyzer = PatternDiscoveryAnalyzer()
    df = analyzer.load_data('enriched_app_dataset.csv')
    if df is None: return

    df_filtered = df[df['label'].isin(['suspicious', 'legitimate'])].copy()

    if len(df_filtered[df_filtered['label'] == 'suspicious']) == 0:
        print("Nie znaleziono aplikacji oznaczonych jako 'suspicious'. Zakończono analizę.")
        return
    if len(df_filtered[df_filtered['label'] == 'legitimate']) == 0:
        print("Nie znaleziono aplikacji oznaczonych jako 'legitimate'. Zakończono analizę.")
        return

    analyzer.discover_suspicious_keywords_tfidf(df_filtered)
    analyzer.download_threshold = analyzer.discover_numerical_patterns(df_filtered, 'installs_numeric', 'Liczba Pobrań')
    analyzer.age_threshold = analyzer.discover_numerical_patterns(df_filtered, 'age_days', 'Wiek Aplikacji')
    analyzer.discover_domain_patterns(df_filtered)
    
    analyzer.create_visualizations(df_filtered)
    analyzer.generate_final_report()
    
    print("\n" + "="*80 + "\nANALIZA ZAKOŃCZONA\n" + "="*80)

if __name__ == "__main__":
    main()