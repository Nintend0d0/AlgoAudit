import os
import yaml
import pandas as pd
import warnings

# Suppress the FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

KEYWORD_FILE = "input/keywords.yml"
INPUT_FOLDER = "input"
ANOVA_FILE = "output/anova.csv"

# *** Prepare Data

# Load our search term lists and filter by actually scraped keyword groups
keyword_cols = ['group','keyword','category']
categories = ["male", "female", "neutral"]

scraped_keywords = pd.DataFrame(columns=keyword_cols)
keyword_groups = yaml.safe_load(open(KEYWORD_FILE))

for group, keywords in keyword_groups.items():
    filepath = os.path.join(INPUT_FOLDER, f"{group}.csv")
    if os.path.isfile(filepath):
        group_label = [group for x in keywords]
        category = [categories[x] if x < len(categories) else "-" for x in range(len(keywords))]
        temp_df = pd.DataFrame(list(zip(group_label, keywords, category)), columns=keyword_cols)
        scraped_keywords = pd.concat([scraped_keywords, temp_df], ignore_index=True)

# scraped_keywords now contains all keyword groups for which a scrape file exists, together with the
# gender-specific keywords and their corresponding category.

# Prepare dataframe to perform statistics
anova_cols = ['site', 'group','keyword','category', 'recall']
anova_df = pd.DataFrame(columns=anova_cols)

groups = scraped_keywords['group'].unique()

for group in groups:
    group_df = scraped_keywords[scraped_keywords['group'] == group]
    group_keywords = group_df['keyword'].unique()

    csv_file = os.path.join(INPUT_FOLDER, f"{group}.csv")
    results_df = pd.read_csv(csv_file)

    sites = results_df['site'].unique()

    for site in sites:
        temp_df = group_df.copy()
        temp_df['site'] = site
        temp_df['recall'] = 0.0

        # Calculate recall
        site_df = results_df.loc[(results_df['site'] == site)]
        total_unique_jobs = len(set(site_df['job ad id'].unique()))

        if total_unique_jobs > 0:
            temp_df['recall'] = temp_df['keyword'].apply(lambda kw:
                                                            site_df[site_df['keyword'] == kw].drop_duplicates(
                                                                subset='job ad id').shape[0] / total_unique_jobs
                                                            )
        anova_df = pd.concat([anova_df, temp_df], ignore_index=True)

anova_df.sort_values(by=['site', 'group'], inplace=True, ignore_index=True)
print(anova_df)

# Store the ANOVA statistics df into a csv file.
anova_df.to_csv(ANOVA_FILE, index=False)

