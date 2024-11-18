from autoload import ModuleLoader
import yaml
from tqdm import tqdm
import csv
import os.path
import urllib.parse
import time

start_time = time.time()

# Our scraper "interface" and our CSV fieldnames
from Scraper import Scraper, fieldnames

# Imports all classes from ./scrapers
scraper_classes = ModuleLoader().load_classes("scrapers")

# load configresults
unsave_config = yaml.safe_load(open("input/config.yml"))

# escape location name
unsave_config["location"]["name"] = urllib.parse.quote(
    unsave_config["location"]["name"]
)

CONFIG = unsave_config

# load our search term lists
KEYWORD_GROUPS = yaml.safe_load(open("input/keywords.yml"))

# create output files
for group in KEYWORD_GROUPS:
    filepath = f"ouput/{group}.csv"
    if not os.path.isfile(filepath):
        print(f'Filepath "{filepath}" not found! Creating...')
        csv.DictWriter(open(filepath, "a"), fieldnames).writeheader()

# TODO: Check for correctness
# keep track of progress
previous_progress = {"keywords": set(), "pages": set()}
for group in KEYWORD_GROUPS:
    # Read the CSV file
    with open(f"ouput/{group}.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            previous_progress["keywords"].add(row["keyword"])
            previous_progress["pages"].add(row["page"])

# for nice output
statistics = {"total": 0, "success": 0, "failed": 0}

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
            statistics["total"] += 1

            # changes scraper type from unknonw to our interface
            scraper: Scraper = SC(group_progress.write, CONFIG)

            keyword_progress.set_postfix_str(scraper.NAME)

            # skip already scraped keywords and pages
            if (
                previous_progress["keywords"]
                and previous_progress["pages"]
                and keyword in previous_progress["keywords"]
                and scraper.NAME in previous_progress["pages"]
            ):
                group_progress.write(f"Skipping '{keyword}' on '{scraper.NAME}'!")
                continue

            group_progress.write(f"Scraping for '{keyword}' on '{scraper.NAME}'.")

            # does the request (the keyword has to be url safe)
            response = scraper.fetch(urllib.parse.quote(keyword))

            # COMMENT ME - temporary sleep, to prevent blockage while testing
            # time.sleep(2)

            # "handle" errors
            if response.status_code != 200:
                group_progress.write(
                    f"ERROR! While getting '{keyword}' on '{scraper.NAME}'."
                )
                group_progress.write(
                    f"Code: {response.status_code} Message: {response.reason}."
                )
                open("ouput/error.log", "a").write(
                    f"{time.strftime("%Y-%m-%d %H:%M:%S")}\tERROR! While getting  '{keyword}' on  '{scraper.NAME}'. Code: {response.status_code} Message:  {response.reason}.\n"
                )
                # just continue, ideally we will just be able to re-run later.
                statistics["failed"] += 1
                continue

            # parses using beautifulsoup
            results = scraper.parse(response.text)

            def include_additional_headers(row):
                row["keyword"] = keyword
                row["page"] = scraper.NAME
                return row

            rows = map(include_additional_headers, results)

            # store to csv, ideally as a stream (one row at the time)
            csv.DictWriter(open(f"ouput/{group}.csv", "a"), fieldnames).writerows(rows)

            statistics["success"] += 1

end_time = time.time()

print(f"Scraping finished in {round(end_time - start_time, 2)} seconds.")
print(
    f"{statistics["success"]} succeeded and {statistics['failed']} failed of {statistics["total"]} in total."
)
print("See error.log for the failed ones.")
