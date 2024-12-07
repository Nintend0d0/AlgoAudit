import os
from itertools import combinations
from functools import reduce
import csv
from numpy import tile
import yaml
import pandas as pd
from plotly import graph_objs as go

# Job manifest
DO_PRINT_SUMMARY = False
DO_CSV_SUMMARY = True
DO_VISUALIZE = True

# *** Prepare Data

# get all csv files
csv_files = []
for file in os.listdir("input/"):
    if file.endswith(".csv"):
        csv_files.append(file)

# all the interesting values
total_unique_jobs: dict[str, dict[str, set[str]]] = {}
unique_jobs: dict[str, dict[str, set[str]]] = {}
intersect_jobs: dict[str, dict[tuple[str, str] | tuple[str, str, str], set[str]]] = {}

for csv_file in csv_files:
    # for csv_file in ["informatik.csv"]:
    df = pd.read_csv(f"input/{csv_file}")

    group = csv_file.split(".")[0]

    sites = df["site"].unique()

    for site in sites:
        site_df = df.loc[(df["site"] == site)]

        total_unique_jobs.setdefault(group, {})[site] = set(
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

        if len(keywords) == 3:
            job_ids = (
                set(site_df.loc[site_df["keyword"] == keyword]["job ad id"].unique())
                for keyword in keywords
            )

            def reducer(prev: set, current: set) -> set:
                if prev:
                    return prev.intersection(current)
                return current

            triplet = tuple(keywords)
            intersect_jobs.setdefault(site, {})[tuple(keywords)] = reduce(
                reducer, job_ids
            )


# *** print summary
if DO_PRINT_SUMMARY:
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
if DO_CSV_SUMMARY:
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
                if len(keyword_pair) == 3:
                    writer.writerow(
                        [
                            site,
                            f"{keyword_pair[0]} ∩ {keyword_pair[1]} ∩ {keyword_pair[2]}",
                            len(job_ids),
                        ]
                    )
                else:
                    keyword, other_keyword = keyword_pair
                    writer.writerow(
                        [site, f"{keyword} ∩ {other_keyword}", len(job_ids)]
                    )


# *** Visualize
if DO_VISUALIZE:

    KEYWORD_GROUPS = yaml.safe_load(open("input/keywords.yml"))

    for group in KEYWORD_GROUPS:
        if group not in total_unique_jobs:
            continue

        all_sites = set(unique_jobs.keys()) | set(intersect_jobs.keys())

        for site in all_sites:
            bars: list[go.Bar] = []

            # total jobs per site
            """
            bars.append(
                go.Bar(
                    y=[len(total_unique_jobs[group].get(site, {}))],
                    text=[len(total_unique_jobs[group].get(site, {}))],
                    name="Total",
                )
            )
            """

            # unique jobs per keyword
            for keyword in KEYWORD_GROUPS[group]:
                bars.append(
                    go.Bar(
                        y=[len(unique_jobs[site].get(keyword, {}))],
                        text=[len(unique_jobs[site].get(keyword, {}))],
                        name=keyword,
                    )
                )

            # Intersect jobs
            for pair in combinations(KEYWORD_GROUPS[group], 2):
                keyword, other_keyword = pair

                bars.append(
                    go.Bar(
                        y=[len(intersect_jobs[site].get(pair, {}))],
                        text=[len(intersect_jobs[site].get(pair, {}))],
                        name=f"{keyword} ∩ {other_keyword}",
                    )
                )

            all_intersection = tuple(KEYWORD_GROUPS[group])
            if len(all_intersection) == 3:

                bars.append(
                    go.Bar(
                        y=[len(intersect_jobs[site].get(all_intersection, {}))],
                        text=[len(intersect_jobs[site].get(all_intersection, {}))],
                        name=f"{all_intersection[0]} ∩ {all_intersection[1]} ∩ {all_intersection[2]}",
                    )
                )

            """
            if bars:
                bars.sort(key=lambda x: x.y[0], reverse=True)  # type: ignore
            """

            fig = go.Figure(
                data=bars,
                layout=go.Layout(
                    title=f"{group.capitalize()} on {site}",
                    xaxis=go.layout.XAxis(visible=False),
                    yaxis=go.layout.YAxis(title="Count"),
                    barmode="stack",
                ),
            )
            fig.write_image(f"output/{site.replace(".", "-")}_{group}.png")
