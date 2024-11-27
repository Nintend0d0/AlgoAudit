import os
from itertools import combinations
import csv
import pandas as pd
import plotly.express as px

# *** Prepare Data

# get all csv files
csv_files = []
for file in os.listdir("input/"):
    if file.endswith(".csv"):
        csv_files.append(file)

# all the interesting values
total_unique_jobs: dict[str, dict[str, set[str]]] = {}
unique_jobs: dict[str, dict[str, set[str]]] = {}
intersect_jobs: dict[str, dict[tuple[str, str], set[str]]] = {}

for csv_file in csv_files:
    # for csv_file in ["informatik.csv"]:
    df = pd.read_csv(f"input/{csv_file}")

    sites = df["site"].unique()

    for site in sites:
        site_df = df.loc[(df["site"] == site)]

        total_unique_jobs.setdefault(csv_file, {})[site] = set(
            site_df["job ad id"].unique()
        )

        keywords = site_df["keyword"].unique()

        for keyword in keywords:
            job_ids = set(
                site_df.loc[site_df["keyword"] == keyword]["job ad id"].unique()
            )
            all_other_job_ids = set(
                site_df.loc[site_df["keyword"] != keyword]["job ad id"].unique()
            )
            unique_jobs.setdefault(site, {})[keyword] = job_ids - all_other_job_ids

        for pair in combinations(keywords, 2):
            keyword, other_keyword = pair
            job_ids = set(
                site_df.loc[site_df["keyword"] == keyword]["job ad id"].unique()
            )
            other_jobs = set(
                site_df.loc[site_df["keyword"] == other_keyword]["job ad id"].unique()
            )
            intersect_jobs.setdefault(site, {})[pair] = job_ids.intersection(other_jobs)


# *** print summary
if False:
    print("# Unique jobs per file")
    for csv_file, sites in total_unique_jobs.items():
        print(f"\n## {csv_file}")
        for site, job_ids in sites.items():
            print(f"{site}: {len(job_ids)}")

    print("\n# Unique jobs")
    for site, keywords in unique_jobs.items():
        print(f"\n## {site}")
        for keyword, job_ids in keywords.items():
            print(f"{keyword}: {len(job_ids)}")

    print("\n# Intersect jobs")
    for site, keywords in intersect_jobs.items():
        print(f"\n## {site}")
        for keyword_pair, job_ids in keywords.items():
            keyword, other_keyword = keyword_pair
            print(f"{keyword} ∩ {other_keyword}: {len(job_ids)}")


# *** csv summary
if True:
    with open(f"output/unique_jobs_per_file.csv", "w") as file:
        writer = csv.writer(file)

        writer.writerow(["file", "site", "count"])

        for csv_file, sites in total_unique_jobs.items():
            for site, job_ids in sites.items():
                writer.writerow([csv_file, site, len(job_ids)])

    with open(f"output/unique_jobs.csv", "w") as file:
        writer = csv.writer(file)

        writer.writerow(["site", "keyword", "count"])

        for site, keywords in unique_jobs.items():
            for keyword, job_ids in keywords.items():
                writer.writerow([site, keyword, len(job_ids)])

    with open(f"output/intersect_jobs.csv", "w") as file:
        writer = csv.writer(file)

        writer.writerow(["site", "keyword", "count"])

        for site, keywords in intersect_jobs.items():
            for keyword_pair, job_ids in keywords.items():
                keyword, other_keyword = keyword_pair
                writer.writerow([site, f"{keyword} ∩ {other_keyword}", len(job_ids)])


# *** Visualize
if True:
    for site, keywords in unique_jobs.items():
        keywords_iter = iter(keywords.items())
        for keyword, job_ids in keywords_iter:
            x, y = [], []
            for _ in range(3):
                x.append(keyword)
                y.append(len(job_ids))
                keyword, job_ids = next(keywords_iter)

            fig = px.bar(x=x, y=y)
            fig.update_layout({"xaxis_title": "Job", "yaxis_title": "Count"})
            fig.write_image(
                f"output/{site.replace(".", "-")}_{"+".join(map(lambda s: s.replace(" ", "-"), x))}.png"
            )


# FIXME: Job-groups are messed up!
