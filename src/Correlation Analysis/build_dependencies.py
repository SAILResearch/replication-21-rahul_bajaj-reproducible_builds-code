import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.stats.contingency import association
import warnings
warnings.filterwarnings("ignore")


def main():
  # Load Tables`
  distributions_tbl = pd.read_csv("../../data/distributions.csv", sep=",")
  stats_build = pd.read_csv("../../data/stats_build.csv", sep=',')
  package_dep_tbl = pd.read_csv("../../data/debian_dependency_graph_tbl.csv", sep=",")
  stats_build_mod = pd.merge(stats_build, distributions_tbl, left_on="distribution", right_on="id")

  package_dep_tbl_subset = package_dep_tbl[package_dep_tbl['packages'] != package_dep_tbl['dependencies']]
  stats_build_filtered_debian = stats_build_mod[(stats_build_mod["name_y"] == "debian")]
  stats_build_filtered = stats_build_filtered_debian[stats_build_filtered_debian["architecture"] == "amd64"]
  stats_build_filtered = stats_build_filtered[stats_build_filtered["suite"] == 'unstable']
  stats_build_sorted = stats_build_filtered.sort_values(by='build_date', ascending=False)
  stats_build_sorted['trim_date'] = pd.to_datetime(stats_build_sorted['build_date']).dt.date
  stats_build_sorted = stats_build_sorted.drop(['id_x', 'id_y', 'distribution'], axis=1)

  # Get the latest instance of the package.
  stats_build_sorted_first_instance = stats_build_sorted.groupby("name_x").first().reset_index()
  stats_build_sorted_first_instance = stats_build_sorted_first_instance.rename(columns={'name_x': 'packages'})

  pkg_deb_merge_stats_build = pd.merge(package_dep_tbl_subset, stats_build_sorted_first_instance, how='left',
                                       left_on='packages', right_on='packages', validate='m:1')
  deb_status = []
  for dependency in pkg_deb_merge_stats_build['dependencies']:
    try:
      package = stats_build_sorted_first_instance[stats_build_sorted_first_instance['packages'] == dependency]
      status = package['status']
      deb_status.append(status.item())
    except:
      deb_status.append(np.nan)
  pkg_deb_merge_stats_build['dependency status'] = deb_status

  df = pkg_deb_merge_stats_build[["packages", "status", "dependencies", "dependency status"]]
  df1 = df.dropna(subset=["dependency status"], inplace=False)

  df1.loc[df1['status'] == 'reproducible', 'status'] = 1
  df1.loc[df1['status'] != 1, 'status'] = 0
  df1.loc[df1['dependency status'] == 'reproducible', 'dependency status'] = 1
  df1.loc[df1['dependency status'] != 1, 'dependency status'] = 0

  df2 = df1.groupby(['packages', 'status'], as_index=False).agg({'dependency status': 'min'})
  dataset_tbl = pd.crosstab(df2.status, df2['dependency status'])
  observed_values = dataset_tbl.values
  print("Observed Values :-\n", observed_values)

  stat, p, dof, expected = stats.chi2_contingency(dataset_tbl)
  print("Values of chi-quare statistics is: %f \n" % stat)
  print(f"p-value is: {p:.20f} \n")
  print("Effect size: \n", association(dataset_tbl, method="cramer"))

if __name__ == '__main__':
  main()
