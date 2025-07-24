import pandas as pd
from google_play_scraper import app as gp_app
from itunes_app_scraper.scraper import AppStoreScraper
from tqdm import tqdm

# Konfiguracja paska postępu dla biblioteki pandas
tqdm.pandas()

def is_ios_app(app_id):
    """Sprawdza, czy ID aplikacji jest numeryczne (co sugeruje aplikację iOS)."""
    return str(app_id).isdigit()

def scrape_google_play(app_id):
    """Pobiera dane dla pojedynczej aplikacji z Google Play Store."""
    try:
        app_details = gp_app(app_id)
        return {
            'installs': app_details.get('installs'),
            'releaseDate': app_details.get('released'),
            'developer': app_details.get('developer'),
            'developerId': app_details.get('developerId'),
            'developerWebsite': app_details.get('developerWebsite'),
            'source': 'Google Play',
            'error': None
        }
    except Exception as e:
        return {
            'installs': None, 'releaseDate': None, 'developer': None,
            'developerId': None, 'developerWebsite': None, 'source': 'Google Play', 'error': str(e)
        }

def scrape_app_store(app_id):
    """
    Pobiera dane dla pojedynczego ID aplikacji z App Store, używając
    poprawnej metody i nazw pól z dostarczonej dokumentacji.
    """
    try:
        scraper = AppStoreScraper()
        # Ta metoda zwraca generator, nawet dla jednego ID, więc musimy go obsłużyć
        app_details_iterator = scraper.get_multiple_app_details([app_id])
        # Pobieramy pierwszy (i jedyny) wynik z generatora
        app_details = next(app_details_iterator, None)

        if app_details:
            # Używamy poprawnych nazw pól z pliku example.txt
            return {
                'installs': 'Not Available',
                'releaseDate': app_details.get('releaseDate'),
                'developer': app_details.get('sellerName'),
                'developerId': str(app_details.get('artistId')),
                'developerWebsite': app_details.get('sellerUrl'),
                'source': 'App Store',
                'error': None
            }
        else:
            return {
                'installs': None, 'releaseDate': None, 'developer': None,
                'developerId': None, 'developerWebsite': None, 'source': 'App Store', 'error': 'App not found'
            }
    except Exception as e:
         return {
            'installs': None, 'releaseDate': None, 'developer': None,
            'developerId': None, 'developerWebsite': None, 'source': 'App Store', 'error': str(e)
        }

def process_app_id(app_id):
    """Przetwarza pojedyncze ID, kierując je do odpowiedniego scrapera."""
    if pd.notna(app_id) and isinstance(app_id, (str, int)):
        app_id_str = str(app_id)
        if is_ios_app(app_id_str):
            return scrape_app_store(app_id_str)
        else:
            return scrape_google_play(app_id_str)
    else:
        return {
            'installs': None, 'releaseDate': None, 'developer': None,
            'developerId': None, 'developerWebsite': None, 'developerDomain': None,
            'source': None, 'error': 'Invalid App ID'
        }

# --- Główna część skryptu ---
try:
    df = pd.read_csv('appstore_apps.csv')

    print("Rozpoczynam pobieranie danych dla aplikacji. To może zająć kilka minut...")
    print("Uwaga: Dla aplikacji iOS liczba instalacji nie jest dostępna ze względu na politykę App Store.")
    
    scraped_data = df['app_id'].progress_apply(process_app_id)

    scraped_df = pd.DataFrame(scraped_data.tolist())

    enriched_df = pd.concat([df, scraped_df], axis=1)

    output_filename = 'enriched_app_dataset2.csv'
    enriched_df.to_csv(output_filename, index=False, encoding='utf-8-sig')

    print(f"\nGotowe! Wzbogacone dane zostały zapisane w pliku: {output_filename}")
    print("\nPodgląd pierwszych 5 wierszy wyników:")
    print(enriched_df.head())
    
    # Statystyki
    print(f"\nStatystyki:")
    print(f"Łączna liczba aplikacji: {len(enriched_df)}")
    print(f"Aplikacje Google Play: {len(enriched_df[enriched_df['source'] == 'Google Play'])}")
    print(f"Aplikacje App Store: {len(enriched_df[enriched_df['source'] == 'App Store'])}")
    print(f"Aplikacje z błędami: {len(enriched_df[enriched_df['error'].notna()])}")

except FileNotFoundError:
    print("Błąd: Plik 'training_dataset.csv' nie został znaleziony w bieżącym folderze.")
except Exception as e:
    print(f"Wystąpił nieoczekiwany błąd: {e}")