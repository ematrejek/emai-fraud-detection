# 3_audit_sample.py
import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
import urllib.parse
from thefuzz import fuzz
from google_play_scraper import app as gp_app
from itunes_app_scraper.scraper import AppStoreScraper
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Klasa AdvancedRuleScorer z ostatniej, poprawionej wersji
class AdvancedRuleScorer:
    # ... (cała, ostatnia wersja klasy AdvancedRuleScorer) ...
    def __init__(self, rules_path='advanced_rules.json'):
        try:
            with open(rules_path, 'r', encoding='utf-8') as f: self.rules = json.load(f)
            self.base_weights = {'app_keyword': 0.5, 'domain_keyword': 0.2, 'age': 0.15, 'downloads': 0.15}
        except FileNotFoundError:
            print(f"BŁĄD KRYTYCZNY: Nie znaleziono pliku reguł '{rules_path}'."); self.rules = None

    def _scrape_app_data(self, app_id: str):
        try:
            if str(app_id).isdigit():
                scraper = AppStoreScraper(); details = scraper.get_app_details(app_id, country='us')
                return {'appName': details.get('trackName'), 'releaseDate': details.get('releaseDate'), 'developerWebsite': details.get('sellerUrl')}
            else:
                details = gp_app(app_id, lang='en', country='us')
                return {'appName': details.get('title'), 'releaseDate': details.get('released'), 'developerWebsite': details.get('developerWebsite'), 'installs': details.get('installs')}
        except Exception: return {}

    def _get_keyword_score(self, text: str, keyword_type: str):
        if pd.isna(text): return None
        keyword_map = self.rules.get('app_keywords' if keyword_type == 'app' else 'domain_keywords', {})
        text_words = re.findall(r'[a-z]+', text.lower())
        max_score = 0.0
        for word in text_words:
            for suspicious_word, score in keyword_map.items():
                if fuzz.ratio(word, suspicious_word) > 90:
                    if score > max_score: max_score = score
        return max_score

    def _get_numerical_score(self, value, threshold):
        if pd.isna(value) or threshold is None: return None
        if value > threshold: return 0.0
        return max(0, 1.0 - (value / threshold))

    def predict_and_explain(self, app_id: str):
        if not self.rules: return None
        scraped_data = self._scrape_app_data(app_id)
        text_to_analyze = scraped_data.get('appName') if str(app_id).isdigit() else app_id
        domain_to_analyze = scraped_data.get('developerWebsite')
        installs_raw = scraped_data.get('installs')
        installs_numeric = pd.to_numeric(str(installs_raw).replace('+', '').replace(',', ''), errors='coerce') if pd.notna(installs_raw) else np.nan
        age_days = np.nan
        release_date = scraped_data.get('releaseDate')
        if pd.notna(release_date):
            for fmt in ['%b %d, %Y', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d']:
                try: age_days = (datetime.now() - datetime.strptime(str(release_date), fmt)).days; break
                except: continue
        app_keyword_score = self._get_keyword_score(text_to_analyze, 'app')
        domain_keyword_score = self._get_keyword_score(domain_to_analyze, 'domain')
        age_score = self._get_numerical_score(age_days, self.rules.get('age_threshold'))
        download_score = self._get_numerical_score(installs_numeric, self.rules.get('download_threshold'))
        final_scores = {'app_keyword': 0.5 if app_keyword_score is None else app_keyword_score, 'domain_keyword': 0.5 if domain_keyword_score is None else domain_keyword_score, 'age': 0.5 if age_score is None else age_score, 'downloads': 0.5 if download_score is None else download_score}
        if str(app_id).isdigit() and not scraped_data: final_scores = {'app_keyword': 0.5, 'domain_keyword': 0.5, 'age': 0.5, 'downloads': 0.5}
        final_probability = sum(self.base_weights[key] * final_scores[key] for key in self.base_weights)
        return {'app_id': app_id, 'final_suspicion_probability': min(final_probability, 1.0), **final_scores, **self.base_weights}

def main():
    INPUT_FILE = '53755.csv'
    OUTPUT_FILE = 'audit_results-53755.csv'

    scorer = AdvancedRuleScorer()
    if not scorer.rules: return
    try:
        input_df = pd.read_csv(INPUT_FILE)
        if 'app_id' not in input_df.columns: print(f"BŁĄD: Plik '{INPUT_FILE}' musi zawierać kolumnę 'app_id'."); return
    except FileNotFoundError: print(f"BŁĄD: Nie znaleziono pliku wejściowego '{INPUT_FILE}'."); return

    tqdm.pandas(desc="Audytowanie aplikacji")
    audit_results = input_df['app_id'].progress_apply(scorer.predict_and_explain)
    
    results_df = pd.DataFrame(audit_results.tolist())
    results_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"\nAudyt zakończony. Szczegółowe wyniki zapisano w pliku: '{OUTPUT_FILE}'")

if __name__ == "__main__":
    main()