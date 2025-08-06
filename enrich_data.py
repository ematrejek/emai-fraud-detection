import pandas as pd
import os
from tqdm import tqdm
from datetime import datetime
from google_play_scraper import app as gp_app
from itunes_app_scraper.scraper import AppStoreScraper
import warnings
warnings.filterwarnings('ignore')

tqdm.pandas(desc="Wzbogacanie danych")

def scrape_app_data(app_id):
    """Pobiera dane dla pojedynczej aplikacji z odpowiedniego sklepu."""
    try:
        if str(app_id).isdigit(): # Aplikacja iOS
            scraper = AppStoreScraper()
            details = scraper.get_app_details(app_id, country='us')
            return {
                'app_id': app_id, 'source': 'App Store', 'appName': details.get('trackName'),
                'releaseDate': details.get('releaseDate'), 'developerWebsite': details.get('sellerUrl'), 'installs': None
            }
        else: # Aplikacja Android
            details = gp_app(app_id, lang='en', country='us')
            return {
                'app_id': app_id, 'source': 'Google Play', 'appName': details.get('title'),
                'releaseDate': details.get('released'), 'developerWebsite': details.get('developerWebsite'), 'installs': details.get('installs')
            }
    except Exception:
        return {'app_id': app_id, 'source': None, 'appName': None, 'releaseDate': None, 'developerWebsite': None, 'installs': None}

def main():
    INPUT_FILE = 'training_dataset.csv'
    OUTPUT_FILE = 'enriched_dataset.csv'

    try:
        input_df = pd.read_csv(INPUT_FILE)
        if 'app_id' not in input_df.columns or 'label' not in input_df.columns:
            print(f"BŁĄD: Plik '{INPUT_FILE}' musi zawierać kolumny 'app_id' oraz 'label'.")
            return
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku wejściowego '{INPUT_FILE}'.")
        return

    # Przetwarzamy wszystkie aplikacje, ponieważ łączymy wyniki na końcu
    app_ids_to_process = input_df['app_id'].dropna().unique().tolist()
    
    print(f"Do przetworzenia jest {len(app_ids_to_process)} unikalnych aplikacji.")
    
    apps_df_to_process = pd.DataFrame(app_ids_to_process, columns=['app_id'])
    
    # Krok 1: Pobierz surowe dane
    scraped_results_list = apps_df_to_process['app_id'].progress_apply(scrape_app_data).tolist()
    scraped_df = pd.DataFrame(scraped_results_list)

    # *** NOWA, KLUCZOWA CZĘŚĆ: Przetwarzanie pobranych danych ***
    print("Przetwarzanie pobranych danych (obliczanie wieku, konwersja pobrań)...")

    # Funkcja do konwersji daty na wiek w dniach
    def to_days(date_str):
        if pd.isna(date_str): return None
        for fmt in ['%b %d, %Y', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d']:
            try:
                # Używamy tz_localize(None), aby usunąć strefę czasową i uniknąć błędów
                dt_obj = pd.to_datetime(date_str, format=fmt).tz_localize(None)
                return (datetime.now() - dt_obj).days
            except (ValueError, TypeError):
                continue
        return None
        
    scraped_df['age_days'] = scraped_df['releaseDate'].apply(to_days)

    # Funkcja do konwersji instalacji na liczbę
    scraped_df['installs_numeric'] = pd.to_numeric(
        scraped_df['installs'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce'
    )

    # Krok 2: Połącz oryginalne dane (z 'label') z nowymi, przetworzonymi danymi
    # Używamy `left join`, aby zachować wszystkie wiersze z oryginalnego pliku wejściowego
    final_df = pd.merge(input_df, scraped_df, on='app_id', how='left')

    final_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"\nZakończono wzbogacanie danych. Wyniki zapisano w '{OUTPUT_FILE}'.")
    print("Plik zawiera teraz wszystkie wymagane kolumny, w tym 'age_days' i 'installs_numeric'.")

if __name__ == "__main__":
    main()