from itunes_app_scraper.scraper import AppStoreScraper

scraper = AppStoreScraper()
results = scraper.get_app_ids_for_query("fortnite")
similar = scraper.get_similar_app_ids_for_app(results[0])

app_details = scraper.get_multiple_app_details(similar)
print(list(app_details))