from autoload import ModuleLoader

# Our scraper "interface"
from Scraper import Scraper

# Imports all classes from ./scrapers
scraper_classes = ModuleLoader().load_classes("scrapers")

# load our search term lists

# loop trough it (using tqdm to show process, dont forget total=len(csv) * len(scraper_classes))
# a good thing is, when we always go one site after the other, we automatically have some cooldown


for SC in scraper_classes:

    # changes scraper type from unknonw to our interface
    scraper: Scraper = SC()

    print(f'Scraping "{scraper.NAME}".')

    # does the request
    repsponse = scraper.fetch("search therm")

    # handle errors

    # parses using beautifulsoup
    scraper.parse("repsponse.content")

    # store to csv(?), ideally as a stream (one row at the time)

# Ouput, all pages get their own csv file
# Example header of jobs-ch.csv
# portal, keyword, position, salary, ...
