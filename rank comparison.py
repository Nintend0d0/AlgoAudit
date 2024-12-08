import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr, kendalltau
import os
import matplotlib
matplotlib.use('Agg')

# specify folder containing csv files (insert own folder paths pls)
input_folder_path = r"correlations/input" # TODO: insert folder path where scraping output (= input for this) is saved
output_folder_path = r"correlations" # TODO: insert folder path where rank comparison graphs should be saved

KENDAL_PATH = os.path.join(output_folder_path, "correlation/kendall")
SPEARMAN_PATH = os.path.join(output_folder_path, "correlation/spearman")
SCATTER_PATH = os.path.join(output_folder_path, "scatter")
# create output folders if they do not exist
os.makedirs(KENDAL_PATH, exist_ok=True)
os.makedirs(SPEARMAN_PATH, exist_ok=True)
os.makedirs(SCATTER_PATH, exist_ok=True)

# process each file in the directory
file_list = [f for f in os.listdir(input_folder_path) if f.endswith('.csv')]
for file_name in file_list:
    job_group = os.path.splitext(file_name)[0]
    print(f"Plotting stats for {job_group}")

    file_path = os.path.join(input_folder_path, file_name)
    data = pd.read_csv(file_path)

    # create output folder named after the csv file for easier overview
    #output_folder = os.path.join(output_folder_path, job_group)
    #os.makedirs(output_folder, exist_ok=True)

    # extract relevant columns
    columns_of_interest = ['keyword', 'site', 'page', 'job ad id', 'rank']
    data = data[columns_of_interest].dropna(subset=['rank'])
    data['rank'] = pd.to_numeric(data['rank'], errors='coerce')

    # determine number of ads per page
    ads_per_page = data.groupby(['site', 'page'])['rank'].max().max() + 1

    # compute global ranks by site and keyword
    data['global_rank'] = data.groupby(['site', 'keyword'])['page'].transform(
        lambda x: (x - 1) * ads_per_page
    ) + data['rank']

    # analyze correlations per site
    sites = data['site'].unique()

    for site in sites:
        site_data = data[data['site'] == site]

        # pivot data for rank correlation
        pivoted = site_data.pivot_table(index=['job ad id'], columns='keyword', values='global_rank')

        if pivoted.empty or pivoted.isnull().all().all():
            print(f"skipping site '{site}' in file '{file_name}' due to lack of valid data.")
            continue

        # compute correlations
        spearman_corr = pivoted.corr(method='spearman')
        kendall_corr = pivoted.corr(method=lambda x, y: kendalltau(x, y)[0])

        # save spearman correlation heatmap
        plt.figure(figsize=(8, 6))
        sns.heatmap(spearman_corr, annot=True, cmap='coolwarm', cbar=True)
        plt.title(f"spearman rank correlation (global ranks per keyword) - {site}")
        spearman_file = os.path.join(SPEARMAN_PATH, f"{site}_{job_group}-spearman_correlation.png")
        plt.savefig(spearman_file, bbox_inches='tight')
        plt.close()

        # save kendall correlation heatmap
        plt.figure(figsize=(8, 6))
        sns.heatmap(kendall_corr, annot=True, cmap='coolwarm', cbar=True)
        plt.title(f"kendall rank correlation (global ranks per keyword) - {site}")
        kendall_file = os.path.join(KENDAL_PATH, f"{site}_{job_group}-kendall_correlation.png")
        plt.savefig(kendall_file, bbox_inches='tight')
        plt.close()

        # save scatter plots for rank comparison
        search_terms = pivoted.columns
        for i, term1 in enumerate(search_terms):
            for term2 in search_terms[i+1:]:
                plt.figure(figsize=(6, 6))
                plt.scatter(pivoted[term1], pivoted[term2], alpha=0.7)
                plt.title(f"rank comparison: {term1} vs {term2} - {site}")
                plt.xlabel(f"global rank ({term1})")
                plt.ylabel(f"global rank ({term2})")

                # plot diagonal references
                plt.axline((0, 0), slope=1, color='red', linestyle='dashed', label="perfect agreement")

                x_min, x_max = plt.gca().get_xlim()
                y_min, y_max = plt.gca().get_ylim()

                diag_min = min(x_min, y_min)
                diag_max = max(x_max, y_max)

                plt.axline((x_min, y_min), (x_max, y_max), color='blue', linestyle='dotted', label="true diagonal")

                plt.legend()
                scatter_file = os.path.join(SCATTER_PATH, f"{site}_{job_group}-{term1}_vs_{term2}_scatter.png")
                plt.savefig(scatter_file, bbox_inches='tight')
                plt.close()
