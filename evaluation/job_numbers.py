import os
from itertools import combinations
from functools import reduce
import csv
from numpy import tile
import yaml
import pandas as pd
from plotly import graph_objs as go
from pathlib import Path

# Job manifest
DO_PRINT_SUMMARY = False
DO_CSV_SUMMARY = True
DO_VISUALIZE = True

# File and folder locations
KEYWORD_FILE = "input/keywords.yml"
CSV_OUT_PATH = "output"
VIZ_OUT_PATH = "output/viz"

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
    df = pd.read_csv(f"input/{csv_file}")

    group = csv_file.split(".")[0]

    sites = df["site"].unique()

    for site in sites:
        site_df = df.loc[(df["site"] == site)]

        total_unique_jobs.setdefault(group, {})[site] = set(
            site_df["job ad id"].unique()
        )

        keywords = site_df["keyword"].unique()

        # Determine job ad ids for each search term
        results_per_keyword: dict[str, set[str]] = {}
        for keyword in keywords:
            results_per_keyword.setdefault(keyword, set(
                site_df.loc[site_df["keyword"] == keyword]["job ad id"].unique()
            ))

        # Determine which job ad was returned for which keyword(s) by applying set theory.
        # 1) Job ads returned for one keyword only:
        for keyword in keywords:
            all_sets = [res for kw, res in results_per_keyword.items() if kw != keyword]
            all_sets.insert(0, results_per_keyword[keyword])
            unique_jobs.setdefault(site, {})[keyword] = reduce(lambda a, b: a - b, all_sets)
        # 2) Job ads returned for exactly 2 keywords:
        for keyword_set in combinations(results_per_keyword, 2):
            all_sets = [res for kw, res in results_per_keyword.items() if kw not in keyword_set]
            all_sets.insert(0, results_per_keyword[keyword_set[0]]
                            .intersection(results_per_keyword[keyword_set[1]]))
            intersect_jobs.setdefault(site, {})[keyword_set] = reduce(lambda a, b: a - b, all_sets)
        # 3) Job ads returned for all keywords:
        if len(keywords) == 3:
            intersect_jobs.setdefault(site, {})[tuple(keywords)] = (
                reduce(lambda a, b: a.intersection(b), results_per_keyword.values())
            )

        """
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
        """


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
    out_filepath = os.path.join(CSV_OUT_PATH, "jobs_per_group.csv")
    with open(out_filepath, "w") as file:
        writer = csv.writer(file)

        writer.writerow(["file", "site", "count"])

        for csv_file, sites in total_unique_jobs.items():
            for site, job_ids in sites.items():
                writer.writerow([csv_file, site, len(job_ids)])

    out_filepath = os.path.join(CSV_OUT_PATH, "jobs_per_keyword_combination.csv")
    with open(out_filepath, "w") as file:
        writer = csv.writer(file)

        writer.writerow(["file", "site", "count"])

        for site, keywords in unique_jobs.items():
            for keyword, job_ids in keywords.items():
                writer.writerow([site, keyword, len(job_ids)])

        for site, keywords in intersect_jobs.items():
            for keyword_pair, job_ids in keywords.items():
                writer.writerow([site, " ∩ ".join(keyword_pair), len(job_ids)])


# *** Visualize
if DO_VISUALIZE:

    KEYWORD_GROUPS = yaml.safe_load(open(KEYWORD_FILE))

    # Create output folder if necessary
    Path(VIZ_OUT_PATH).mkdir(parents=True, exist_ok=True)

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
                n = len(unique_jobs[site].get(keyword, {}))
                bars.append(
                    go.Bar(
                        y=[n],
                        text=[n],
                        name=f"{keyword} ({n})",
                    )
                )

            # Intersect jobs
            for pair in combinations(KEYWORD_GROUPS[group], 2):
                n = len(intersect_jobs[site].get(pair, {}))
                bars.append(
                    go.Bar(
                        y=[n],
                        text=[n],
                        name=" ∩ ".join(pair) + f" ({n})",
                    )
                )

            all_intersection = tuple(KEYWORD_GROUPS[group])
            if len(all_intersection) == 3:
                n = len(intersect_jobs[site].get(all_intersection, {}))
                bars.append(
                    go.Bar(
                        y=[n],
                        text=[n],
                        name=" ∩ ".join(all_intersection) + f" ({n})",
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
            fig_filename = f"{site.replace(".", "-")}_{group}.png"
            fig_outfile = os.path.join(VIZ_OUT_PATH, fig_filename)
            fig.write_image(fig_outfile)
