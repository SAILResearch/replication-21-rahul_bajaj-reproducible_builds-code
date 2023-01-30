import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.stats.contingency import association
import warnings
warnings.filterwarnings("ignore")


def intersection(lst1, lst2):
  return list(set(lst1) & set(lst2))


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

  # Get the latest instance of the package.
  stats_build_sorted_firstInstance = stats_build_sorted.groupby("name_x").first().reset_index()
  stats_build_sorted_firstInstance = stats_build_sorted_firstInstance.rename(columns={'name_x': 'Package_name'})

  # Preprocess package table :
  package_dep_tbl_subset = package_dep_tbl[package_dep_tbl.name == package_dep_tbl.package]
  package_dep_tbl_subset = package_dep_tbl_subset.drop_duplicates()

  package_stats_merge = pd.merge(package_dep_tbl_subset, stats_build_sorted_firstInstance, how='left', left_on='name',
                                 right_on='Package_name', validate='m:1')
  df = package_stats_merge
  df1 = df.dropna(subset=["Package_name"], inplace=False)

  deb_status = []
  for dependency in df1['dependency']:
    try:
      package = stats_build_sorted_firstInstance[stats_build_sorted_firstInstance['Package_name'] == dependency]
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
  print("Observed Values :-\n", observed_values)

  stat, p, dof, expected = stats.chi2_contingency(dataset_tbl)
  print("Values of chi-quare statistics is: %f \n" % stat)
  print(f"p-value is: {p:.20f} \n")
  print("Effect size: \n", association(dataset_tbl, method="cramer"))


if __name__ == '__main__':
  main()
