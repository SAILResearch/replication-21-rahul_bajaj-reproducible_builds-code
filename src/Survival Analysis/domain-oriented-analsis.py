import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter
from lifelines.plotting import plot_lifetimes
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


def main():
  packages_df = pd.read_csv('../../data/categorized-debian-packages.csv')
  survival_of_unreproducible_packages(packages_df)
  survival_of_reproducible_packages(packages_df)


def survival_of_unreproducible_packages(packages_df):
  suvival_of_unrepro_debian_df = pd.read_csv('../../data/survival_of_unreproducible_debian_df.csv')
  unrepro_categorized_packages_debian_df = suvival_of_unrepro_debian_df.merge(packages_df, on="packages", how="left")
  unrepro_pg_removed_dups = unrepro_categorized_packages_debian_df.dropna(subset=["type"])

  # Filter categories that have less than 75 packages, as 75 consists of 75% of the packages.
  counts = unrepro_pg_removed_dups['type'].value_counts()
  unrepro_pg_filtered = unrepro_pg_removed_dups[~unrepro_pg_removed_dups['type'].isin(counts[counts < 75].index)]

  # Separate crucial and trivial packages
  unrepro_pg_filtered['category'] = np.where(
    unrepro_pg_filtered.type.isin(['math', 'science', 'sound', 'games', 'gnu-r']), 'Trivial', 'Crucial')
  unrepro_survival_df = unrepro_pg_filtered[['event', 'date_diff_days', 'category']]

  for category in unrepro_pg_filtered.category.unique():
    category_df = unrepro_survival_df[unrepro_survival_df.category == category]
    survival_analysis(category_df, category)

  plt.savefig('../../figures/domain-analysis_for_unrepro_packages.pdf', dpi=2000)
  plt.show()

def survival_of_reproducible_packages(packages_df):
  survival_of_reproducible_df = pd.read_csv('../../data/survival_of_reproducible_debian_df.csv')
  rpro_categorized_packages_debian_df = survival_of_reproducible_df.merge(packages_df, on="packages", how="left")
  repro_pg_removed_dups = rpro_categorized_packages_debian_df.dropna(subset=["type"])
  repro_pg_removed_dups['type'].value_counts().describe()

  # Filter categories that have less than 73 packages, as 73 consists of 75% of the packages.
  counts = repro_pg_removed_dups['type'].value_counts()
  repro_pg_filtered = repro_pg_removed_dups[~repro_pg_removed_dups['type'].isin(counts[counts < 73].index)]

  # Separate crucial and trivial packages
  repro_pg_filtered['category'] = np.where(
    repro_pg_filtered.type.isin(['x11', 'math', 'science', 'sound', 'games', 'gnu-r']), 'Trivial', 'Crucial')
  repro_pg_filtered = repro_pg_filtered[['event', 'date_diff_days', 'category']]

  for category in repro_pg_filtered.category.unique():
    category_df = repro_pg_filtered[repro_pg_filtered.category == category]
    survival_analysis(category_df, category)

  plt.savefig('../../figures/domain-analysis_for_repro_packages.pdf', dpi=2000)
  plt.show()


def survival_analysis(df, types):
  plt.rcParams.update({'font.size': 14})
  kmf = KaplanMeierFitter()

  kmf.fit(df['date_diff_days'],
          df['event'],
          label=types)
  int_ax1 = kmf.plot(ci_show=0)

  int_ax1.set_xlabel("Time in Days", fontsize=16)
  int_ax1.set_ylabel("Survival probability", fontsize=16)
  int_ax1.spines['right'].set_visible(False)
  int_ax1.spines['top'].set_visible(False)
  int_ax1.legend(fontsize=14)
  int_ax1.legend()
  plt.vlines(x=360, ymin=0.05, ymax=0.995, color='r', linestyle='--', label='1 year')
  return int_ax1


if __name__ == '__main__':
  main()
