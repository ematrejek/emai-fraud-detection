import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
import urllib.parse
from thefuzz import fuzz
from google_play_scraper import app as gp_app
from itunes_app_scraper.scraper import AppStoreScraper
import warnings
warnings.filterwarnings('ignore')

class AdvancedRuleScorer:
    def __init__(self, rules_path='advanced_rules.json'):
        try:
            print(f"Wczytywanie zaawansowanych reguł z pliku: {rules_path}")
            with open(rules_path, 'r', encoding='utf-8') as f:
                self.rules = json.load(f)
            self.base_weights = {
                'app_keyword': 0.5,
                'domain_keyword': 0.2,
                'age': 0.15,
                'downloads': 0.15
            }
            print("Reguły i wagi gotowe do pracy.")
        except FileNotFoundError:
            print(f"BŁĄD KRYTYCZNY: Nie znaleziono pliku reguł '{rules_path}'.")
            self.rules = None

    def _scrape_app_data(self, app_id: str):
        print(f"Pobieranie danych dla: {app_id}...")
        try:
            if str(app_id).isdigit():
                scraper = AppStoreScraper()
                details = scraper.get_app_details(app_id, country='us')
                return {'appName': details.get('trackName'), 'releaseDate': details.get('releaseDate'), 'developerWebsite': details.get('sellerUrl')}
            else:
                details = gp_app(app_id, lang='en', country='us')
                return {'appName': details.get('title'), 'releaseDate': details.get('released'), 'developerWebsite': details.get('developerWebsite'), 'installs': details.get('installs')}
        except Exception:
            print(f"  > Aplikacja nieznaleziona lub błąd pobierania danych.")
            return {}

    def _get_keyword_score(self, text: str, keyword_type: str):
        # *** ZMIANA: Zwraca None, jeśli brakuje tekstu, aby poprawnie aktywować regułę 50% ***
        if pd.isna(text): 
            return None
        
        keyword_map = self.rules.get('app_keywords' if keyword_type == 'app' else 'domain_keywords', {})
        text_words = re.findall(r'[a-z]+', text.lower())
        
        max_score = 0.0
        for word in text_words:
            for suspicious_word, score in keyword_map.items():
                if fuzz.ratio(word, suspicious_word) > 90:
                    if score > max_score:
                        max_score = score # Znajdź najwyższy wynik
        
        # *** ZMIANA: Zwraca najwyższy znaleziony wynik, a nie średnią ***
        return max_score

    def _get_numerical_score(self, value, threshold):
        if pd.isna(value) or threshold is None:
            return None
        if value > threshold:
            return 0.0
        score = 1.0 - (value / threshold)
        return max(0, score)

    def predict_suspicion(self, app_id: str):
        if not self.rules: return None

        scraped_data = self._scrape_app_data(app_id)
        
        text_to_analyze = scraped_data.get('appName') if str(app_id).isdigit() else app_id
        domain_to_analyze = scraped_data.get('developerWebsite')
        installs = pd.to_numeric(str(scraped_data.get('installs')).replace('+', '').replace(',', ''), errors='coerce') if scraped_data.get('installs') else np.nan
        
        age_days = np.nan
        release_date = scraped_data.get('releaseDate')
        if pd.notna(release_date):
            for fmt in ['%b %d, %Y', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d']:
                try:
                    age_days = (datetime.now() - datetime.strptime(str(release_date), fmt)).days
                    break
                except: continue

        app_keyword_score = self._get_keyword_score(text_to_analyze, 'app')
        domain_keyword_score = self._get_keyword_score(domain_to_analyze, 'domain')
        age_score = self._get_numerical_score(age_days, self.rules.get('age_threshold'))
        download_score = self._get_numerical_score(installs, self.rules.get('download_threshold'))

        # Logika "imputacji niepewnością" 50%
        scores = {
            'app_keyword': 0.5 if app_keyword_score is None else app_keyword_score,
            'domain_keyword': 0.5 if domain_keyword_score is None else domain_keyword_score,
            'age': 0.5 if age_score is None else age_score,
            'downloads': 0.5 if download_score is None else download_score
        }
        
        if str(app_id).isdigit() and not scraped_data:
             print("  > Reguła biznesowa: Brak jakichkolwiek danych dla aplikacji iOS. Przypisuję 50% do każdej cechy.")
             scores = {'app_keyword': 0.5, 'domain_keyword': 0.5, 'age': 0.5, 'downloads': 0.5}

        final_probability = sum(self.base_weights[key] * scores[key] for key in self.base_weights)
        
        return min(final_probability, 1.0)

def main():
    scorer = AdvancedRuleScorer()
    if not scorer.rules:
        return
    
    example_apps = [
        'com.facebook.katana',
        '945305983',
        'com.prank.sound.fart.funny',
        '123456789'
    ]
    
    print("\n--- FAZA PREDYKCJI Z ZAAWANSOWANYMI REGUŁAMI (POPRAWIONA LOGIKA) ---")
    for app_id in example_apps:
        prob = scorer.predict_suspicion(app_id)
        if prob is not None:
            print(f"  > Aplikacja '{app_id}' -> Prawdopodobieństwo bycia 'suspicious': {prob:.2%}\n")

if __name__ == "__main__":
    main()