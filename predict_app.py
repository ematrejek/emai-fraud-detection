import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
import urllib.parse
from thefuzz import fuzz
import xgboost as xgb
import joblib
from google_play_scraper import app as gp_app
from itunes_app_scraper.scraper import AppStoreScraper
import warnings
warnings.filterwarnings('ignore')

class AppClassifier:
    def __init__(self, model_path='xgb_model.joblib', patterns_path='patterns_for_model.json'):
        self.model = None
        self.patterns = None
        try:
            print(f"Wczytywanie wytrenowanego modelu z: {model_path}")
            self.model = joblib.load(model_path)
            with open(patterns_path, 'r', encoding='utf-8') as f:
                self.patterns = json.load(f)
            print("Model i reguły gotowe do predykcji.")
        except FileNotFoundError:
            print("BŁĄD: Nie znaleziono plików modelu ('xgb_model.joblib') lub wzorców ('patterns_for_model.json').")
            print("Upewnij się, że najpierw uruchomiłeś skrypt 'build_model.py'.")

    def _scrape_app_data(self, app_id: str):
        print(f"Pobieranie danych dla: {app_id}...")
        try:
            if str(app_id).isdigit():
                scraper = AppStoreScraper()
                details = scraper.get_app_details(app_id, country='us')
                return {'releaseDate': details.get('releaseDate'), 'developerWebsite': details.get('sellerUrl'), 'installs': None}
            else:
                # *** ZMIANA: Dodano jawne określenie języka i kraju dla większej niezawodności ***
                details = gp_app(app_id, lang='en', country='us')
                return {'releaseDate': details.get('released'), 'developerWebsite': details.get('developerWebsite'), 'installs': details.get('installs')}
        except Exception as e:
            print(f"  > Aplikacja nieznaleziona lub błąd pobierania danych.")
            return {}

    def _prepare_single_app_df(self, app_id: str, scraped_data: dict):
        df = pd.DataFrame([scraped_data], columns=['releaseDate', 'developerWebsite', 'installs'])
        df['app_id'] = app_id
        df['installs_numeric'] = pd.to_numeric(df['installs'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce')
        def to_days(date_str):
            if pd.isna(date_str): return np.nan
            for fmt in ['%b %d, %Y', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    dt_obj = pd.to_datetime(date_str, format=fmt, utc=True).tz_convert(None)
                    return (datetime.now() - dt_obj).days
                except: continue
            return np.nan
        df['age_days'] = df['releaseDate'].apply(to_days)
        return df
        
    def _create_features(self, df: pd.DataFrame):
        suspicious_keywords = self.patterns.get('suspicious_keywords', [])
        suspicious_domain_keywords = self.patterns.get('suspicious_domain_keywords', [])
        features = pd.DataFrame(index=df.index)
        for keyword in suspicious_keywords:
            features[f'kw_{keyword}'] = df['app_id'].apply(lambda x: 1 if pd.notna(x) and fuzz.partial_ratio(keyword, str(x)) > 90 else 0)
        for keyword in suspicious_domain_keywords:
            features[f'domain_kw_{keyword}'] = df['developerWebsite'].apply(lambda x: 1 if pd.notna(x) and fuzz.partial_ratio(keyword, str(x)) > 90 else 0)
        features['age_days'] = df['age_days']
        features['installs_numeric'] = df['installs_numeric']
        
        for col in self.model.get_booster().feature_names:
            if col not in features.columns:
                features[col] = 0
        return features[self.model.get_booster().feature_names]

    def predict_suspicion(self, app_id: str):
        if not self.model:
            return None
        scraped_data = self._scrape_app_data(app_id)
        is_not_found = not scraped_data

        if is_not_found:
            app_name_words = re.findall(r'[a-z]+', str(app_id).lower())
            for word in app_name_words:
                if any(fuzz.token_sort_ratio(word, s_word) > 90 for s_word in self.patterns.get('suspicious_keywords',[])):
                    print(f"  > REGUŁA BIZNESOWA: Aplikacja nieznaleziona i zawiera podejrzane słowa. Wysokie ryzyko.")
                    return 0.95
        
        app_df = self._prepare_single_app_df(app_id, scraped_data)
        features = self._create_features(app_df)
        probability = self.model.predict_proba(features)[0][1]
        
        return probability

def main():
    live_classifier = AppClassifier()
    if not live_classifier.model:
        return
    
    example_apps = [
        'com.facebook.katana',
        'com.prank.sound.fart.funny',
        'com.nonexistent.app12345'
    ]
    
    print("\n--- FAZA PREDYKCJI ---")
    for app_id in example_apps:
        prob = live_classifier.predict_suspicion(app_id)
        if prob is not None:
            print(f"  > Aplikacja '{app_id}' -> Prawdopodobieństwo bycia 'suspicious': {prob:.2%}\n")

if __name__ == "__main__":
    main()