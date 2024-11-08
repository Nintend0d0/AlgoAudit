from autoload import ModuleLoader

from Scraper import Scraper

scraper_classes = ModuleLoader().load_classes("scrapers")

for Scraper in scraper_classes:

    scraper = Scraper()

    print(f'Scraping "{scraper.NAME}".')

    scraper.print()
