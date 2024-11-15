from autoload import ModuleLoader
import yaml
from tqdm import tqdm
import csv
import os.path

# Our scraper "interface"
from Scraper import Scraper, fieldnames

# Imports all classes from ./scrapers
scraper_classes = ModuleLoader().load_classes("scrapers")

# load configresults
CONFIG = yaml.safe_load(open("input/config.yml"))

# load our search term lists
KEYWORD_GROUPS = yaml.safe_load(open("input/keywords.yml"))

# create output files
for group in KEYWORD_GROUPS:
    filepath = f"ouput/{group}.csv"
    if not os.path.isfile(filepath):
        print(f'Filepath "{filepath}" not found! Creating...')
        csv.DictWriter(open(filepath, "a"), fieldnames).writeheader()

# loop trough it (using tqdm to show process)
# a good thing is, when we always go one site after the other, we automatically have some cooldown
group_progress = tqdm(KEYWORD_GROUPS, desc="Group")
for group in group_progress:
    group_progress.set_postfix_str(group)

    keyword_progress = tqdm(KEYWORD_GROUPS[group], desc="Keywords", leave=False)
    for keyword in keyword_progress:
        keyword_progress.set_postfix_str(keyword)

        scraper_progress = tqdm(scraper_classes, desc="Scraper", leave=False)
        for SC in scraper_progress:
            # changes scraper type from unknonw to our interface
            scraper: Scraper = SC(group_progress.write, CONFIG)

            keyword_progress.set_postfix_str(scraper.NAME)
            group_progress.write(f"Scraping for '{keyword}' on '{scraper.NAME}'.")

            # does the request
            response = scraper.fetch(keyword)

            # TODO: handle errors

            # parses using beautifulsoup
            results = scraper.parse(response.text)

            def include_additional_headers(row):
                row["keyword"] = keyword
                row["page"] = scraper.NAME
                return row

            rows = map(include_additional_headers, results)

            # store to csv, ideally as a stream (one row at the time)
            csv.DictWriter(open(f"ouput/{group}.csv", "a"), fieldnames).writerows(rows)

# Ouput, all pages get their own csv file
# Example header of jobs-ch.csv
# portal, keyword, position, salary, ...
