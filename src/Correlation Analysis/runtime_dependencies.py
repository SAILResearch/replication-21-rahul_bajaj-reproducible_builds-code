import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.stats.contingency import association
import warnings
warnings.filterwarnings("ignore")


def intersection(lst1, lst2):
  return list(set(lst1) & set(lst2))


def domain_oriented_analysis(df4):
  categorised_pkg_df = pd.read_csv("../../data/categorized-debian-packages.csv")
  df4_categorized = df4.merge(categorised_pkg_df, left_on='package', right_on='packages')
  max_frequency_domains = df4_categorized.type.value_counts().index

  final_dict = {}
  for domain in max_frequency_domains:
    filtered_df = df4_categorized[df4_categorized.type == domain]
    filtered_df.loc[filtered_df['status'] == 'reproducible', 'status'] = 1
    filtered_df.loc[filtered_df['status'] != 1, 'status'] = 0
    filtered_df.loc[filtered_df['dependency status'] == 'reproducible', 'dependency status'] = 1
    filtered_df.loc[filtered_df['dependency status'] != 1, 'dependency status'] = 0
    domain_df = filtered_df.groupby(['packages', 'status'], as_index=False).agg({'dependency status': 'min'})
    dataset_tbl = pd.crosstab(domain_df.status, domain_df['dependency status'])
    stat, p, dof, expected = stats.chi2_contingency(dataset_tbl)
    effect_size = association(dataset_tbl, method="cramer")
    final_dict[domain] = (stat, p, dof, expected, effect_size)

  significant = []
  not_sig = []
  for keys in final_dict.keys():
    if final_dict[keys][1] <= 0.01:
      significant.append(keys)
    else:
      not_sig.append(keys)

  print("\nDomain Analysis:")
  print('Statistically Significant Correlation for distribution: \nDomain: Effect Size')
  for k, v in final_dict.items():
    if k in significant:
      print(k, v[4])
  print('Number of domains with statistically significant correlation: ', len(significant))
  print("-----------------------------------------")

def get_correlation(package_dep_tbl_subset, stats_build_sorted_instance):
  package_stats_merge = pd.merge(package_dep_tbl_subset, stats_build_sorted_instance, how='left', left_on='name',
                                 right_on='Package_name', validate='m:1')
  df = package_stats_merge
  df1 = df.dropna(subset=["Package_name"], inplace=False)

  deb_status = []
  for dependency in df1['dependency']:
    try:
      package = stats_build_sorted_instance[stats_build_sorted_instance['Package_name'] == dependency]
      status = package['status']
      deb_status.append(status.item())
    except:
      deb_status.append(np.nan)

  df1['dependency status'] = deb_status
  df2 = df1[["package", "status", "dependency", "dependency status"]]
  df3 = df2.dropna(subset=["dependency status"], inplace=False)

  df3.loc[df3['status'] == 'reproducible', 'status'] = 1
  df3.loc[df3['status'] != 1, 'status'] = 0
  df3.loc[df3['dependency status'] == 'reproducible', 'dependency status'] = 1
  df3.loc[df3['dependency status'] != 1, 'dependency status'] = 0
  df4 = df3.groupby(['package', 'status'], as_index=False).agg({'dependency status': 'min'})

  dataset_tbl = pd.crosstab(df4.status, df4['dependency status'])
  observed_values = dataset_tbl.values
  print("Correlation Analysis:")
  print("Observed Values :-\n", observed_values)

  stat, p, dof, expected = stats.chi2_contingency(dataset_tbl)
  print("Values of chi-quare statistics is: %f" % stat)
  print(f"p-value is: {p:.20f}")
  print("Effect size: ", association(dataset_tbl, method="cramer"))

  domain_oriented_analysis(df4)

def main():
  # Load Tables
  distributions_tbl = pd.read_csv("../../data/distributions.csv", sep=",")
  stats_build = pd.read_csv("../../data/stats_build.csv", sep=',')
  package_dep_tbl = pd.read_csv("../../data/transitive_dependency.csv", sep=",")

  stats_build_mod = pd.merge(stats_build, distributions_tbl, left_on="distribution", right_on="id")
  stats_build_filtered_debian = stats_build_mod[(stats_build_mod["name_y"] == "debian")]
  stats_build_filtered = stats_build_filtered_debian[stats_build_filtered_debian["architecture"] == "amd64"]
  stats_build_filtered = stats_build_filtered[stats_build_filtered["suite"] == 'unstable']
  stats_build_sorted = stats_build_filtered.sort_values(by='build_date', ascending=False)
  stats_build_sorted['trim_date'] = pd.to_datetime(stats_build_sorted['build_date']).dt.date
  stats_build_sorted = stats_build_sorted.drop(['id_x', 'id_y', 'distribution'], axis=1)

  # Preprocess package table :
  package_dep_tbl_subset = package_dep_tbl[package_dep_tbl.name == package_dep_tbl.package]
  package_dep_tbl_subset = package_dep_tbl_subset.drop_duplicates()

  # Organize builds.
  stats_build_sorted['rank_num'] = stats_build_sorted.groupby("name_x")['trim_date'].rank(method="first",
                                                                                          ascending=False)
  stats_build_sorted = stats_build_sorted.rename(columns={'name_x': 'Package_name'})
  stats_build_sorted_instance = stats_build_sorted[stats_build_sorted['rank_num'] == 1.0]
  get_correlation(package_dep_tbl_subset, stats_build_sorted_instance)
  stats_build_sorted_instance = stats_build_sorted[stats_build_sorted['rank_num'] == 5.0]
  get_correlation(package_dep_tbl_subset, stats_build_sorted_instance)


if __name__ == '__main__':
  main()
