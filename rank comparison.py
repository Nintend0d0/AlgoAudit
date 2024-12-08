import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr, kendalltau
import os
import matplotlib
matplotlib.use('Agg')

# specify folder containing csv files (insert own folderpath pls)
folder_path = r"" # TODO: insert folderpath where scraping output is saved and rank comparison graphs should be saved
file_list = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# process each file in the directory
for file_name in file_list:
    file_path = os.path.join(folder_path, file_name)
    data = pd.read_csv(file_path)

    # create output folder named after the csv file for easier overview
    output_folder = os.path.join(folder_path, os.path.splitext(file_name)[0])
    os.makedirs(output_folder, exist_ok=True)

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
        spearman_path = os.path.join(output_folder, f"{site}_spearman_correlation.png")
        plt.savefig(spearman_path, bbox_inches='tight')
        plt.close()

        # save kendall correlation heatmap
        plt.figure(figsize=(8, 6))
        sns.heatmap(kendall_corr, annot=True, cmap='coolwarm', cbar=True)
        plt.title(f"kendall rank correlation (global ranks per keyword) - {site}")
        kendall_path = os.path.join(output_folder, f"{site}_kendall_correlation.png")
        plt.savefig(kendall_path, bbox_inches='tight')
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
                scatter_path = os.path.join(output_folder, f"{site}_{term1}_vs_{term2}_scatter.png")
                plt.savefig(scatter_path, bbox_inches='tight')
                plt.close()
