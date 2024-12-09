import os
import pingouin as pg
import pandas as pd

ANOVA_FILE = "output/anova.csv"
PREPARATION_SCRIPT = "job_distributions.py"

if not os.path.isfile(ANOVA_FILE):
    exec(open(PREPARATION_SCRIPT).read())

# Load stats file
anova_df = pd.read_csv(ANOVA_FILE)

sites = anova_df['site'].unique()
for site in sites:
    use_correction = False
    print("\n==================================")
    print(f"Testing on {site}:")
    print("==================================")
    site_df = anova_df.loc[(anova_df['site'] == site)]

    # Perform One-way ANOVA
    anova_results = pg.anova(
        data=site_df,
        dv='precision',
        between='category',
        detailed=True,
    )
    p = anova_results['p-unc'].iloc[0]  # Uncorrected p-value

    print("1) One-way ANOVA:")
    print(anova_results)

    if p < 0.05:
        print(f"p = {p} indicates a significant difference between the three keyword versions.")
    else:
        print(f"p = {p} indicates no significant difference.")


    # Perform Repeated Measures ANOVA with Greenhouse-Geisser correction if sphericity is violated
    anova_results = pg.rm_anova(
        data=site_df,
        dv='precision',
        within='category',
        subject='group',
        detailed=True,
    )
    p_unc = anova_results['p-unc'].iloc[0]  # Uncorrected p-value
    p_GG_corr = anova_results['p-GG-corr'].iloc[0]  # Greenhouse-Geisser corrected p-value
    sphericity = anova_results['sphericity'].iloc[0]  # Sphericity of the data (boolean)

    print("\n2) Repeated Measures ANOVA:")
    print(anova_results)

    if sphericity:
        print("\nSphericity assumption holds.")
        p = p_unc
    else:
        print("\nSphericity is violated => apply correction.")
        p = p_GG_corr

    if p < 0.05:
        print(f"p = {p} indicates a significant difference between the three keyword versions.")
    else:
        print(f"p = {p} indicates no significant difference.")

    # Pairwise comparisons
    pairwise = pg.pairwise_tests(
        dv='precision',
        within='category',
        subject='group',
        data=site_df,
        padjust='bonf',
    )
    pairwise['sig'] = pairwise['p-corr'] < 0.05
    pairwise['effect'] = pairwise['hedges'].apply(lambda h: "small" if abs(h) <= 0.2 else "large" if abs(h) >= 0.8 else "medium")
    pairwise['dir'] = pairwise['hedges'].apply(lambda h: "<" if h < 0 else ">" if h >= 0 else "=")

    print("\nPost-hoc pairwise comparisons:")
    print(pairwise)

    print()