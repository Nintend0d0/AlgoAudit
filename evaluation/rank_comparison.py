from itertools import combinations
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# define generalized Kendall's tau computation function
def generalized_kendall_tau(x, y):
    x = np.array(x)
    y = np.array(y)
    mask = ~np.logical_or(np.isnan(x), np.isnan(y))
    x = x[mask]
    y = y[mask]

    if len(x) <= 1 or len(y) <= 1:
        return np.nan

    concordant, discordant = 0, 0

    for i, j in combinations(range(len(x)), 2):
        if (x[i] - x[j]) * (y[i] - y[j]) > 0:
            concordant += 1
        elif (x[i] - x[j]) * (y[i] - y[j]) < 0:
            discordant += 1

    total_pairs = concordant + discordant
    if total_pairs == 0:
        return np.nan

    tau_g = (concordant - discordant) / total_pairs
    return tau_g

# file paths
input_folder_path = "input"
output_folder_path = "output"
KENDALL_PATH = os.path.join(output_folder_path, "correlation/kendall")
SCATTER_PATH = os.path.join(output_folder_path, "scatter")
os.makedirs(KENDALL_PATH, exist_ok=True)
os.makedirs(SCATTER_PATH, exist_ok=True)

# go through each csv file
file_list = [f for f in os.listdir(input_folder_path) if f.endswith(".csv")]
for file_name in file_list:
    job_group = os.path.splitext(file_name)[0]
    print(f"Processing {job_group}...")

    file_path = os.path.join(input_folder_path, file_name)
    data = pd.read_csv(file_path)

    # extract relevant columns
    columns_of_interest = ["keyword", "site", "page", "job ad id", "rank"]
    data = data[columns_of_interest].dropna(subset=["rank"])
    data["rank"] = pd.to_numeric(data["rank"], errors="coerce")

    # calculate global ranks for reasonable comparison
    ads_per_page = data.groupby(["site", "page"])["rank"].max().max() + 1
    data["global_rank"] = (
        data.groupby(["site", "keyword"])["page"].transform(lambda x: (x - 1) * ads_per_page)
        + data["rank"]
    )

    # process each site
    sites = data["site"].unique()

    for site in sites:
        site_data = data[data["site"] == site]
        pivoted = site_data.pivot_table(index="job ad id", columns="keyword", values="global_rank")

        # skip if fewer than 2 keywords, no sensible comparison possible
        if pivoted.shape[1] < 2:
            print(f"Skipping site '{site}' in file '{file_name}' due to insufficient keywords.")
            continue

        # calculate kendall's tau relevant keyword pairs
        search_terms = pivoted.columns
        kendall_corr = pd.DataFrame(
            index=search_terms, columns=search_terms, dtype=float
        )

        for term1, term2 in combinations(search_terms, 2):
            tau_g = generalized_kendall_tau(pivoted[term1], pivoted[term2])
            kendall_corr.loc[term1, term2] = tau_g
            kendall_corr.loc[term2, term1] = tau_g

        np.fill_diagonal(kendall_corr.values, 1.0)

        # save heatmap
        plt.figure(figsize=(8, 6))
        sns.heatmap(kendall_corr, annot=True, cmap="coolwarm", cbar=True)
        plt.title(f"Generalized Kendall's Tau - {site}")
        kendall_file = os.path.join(
            KENDALL_PATH, f"{site}_{job_group}_generalized_kendall_tau.png"
        )
        plt.savefig(kendall_file, bbox_inches="tight")
        plt.close()

        # save scatter plots
        for term1, term2 in combinations(search_terms, 2):
            plt.figure(figsize=(6, 6))
            plt.scatter(pivoted[term1], pivoted[term2], alpha=0.7)
            plt.title(f"Rank Comparison: {term1} vs {term2} - {site}")
            plt.xlabel(f"Global Rank ({term1})")
            plt.ylabel(f"Global Rank ({term2})")
            # plot reference lines
            plt.axline((0, 0), slope=1, color="red", linestyle="dashed", label="perfect agreement")
            x_min, x_max = plt.gca().get_xlim()
            y_min, y_max = plt.gca().get_ylim()
            diag_min = min(x_min, y_min)
            diag_max = max(x_max, y_max)
            plt.axline((x_min, y_min), (x_max, y_max), color='blue', linestyle='dotted', label="true diagonal")
            plt.legend()
            scatter_file = os.path.join(
                SCATTER_PATH, f"{site}_{job_group}_{term1}_vs_{term2}_scatter.png"
            )
            plt.savefig(scatter_file, bbox_inches="tight")
            plt.close()
