import pandas as pd
import scipy.stats as stats
from scipy.stats.contingency import association
import warnings
warnings.filterwarnings("ignore")


def intersection(lst1, lst2):
  return list(set(lst1) & set(lst2))


def main():
  # Load required datasets
  distributions_tbl = pd.read_csv("../../data/distributions.csv", sep=",")
  stats_build = pd.read_csv("../../data/stats_build.csv", sep=',')

  stats_build_mod = pd.merge(stats_build, distributions_tbl, left_on="distribution", right_on="id")
  stats_build_mod = stats_build_mod.drop(columns=['distribution', 'id_y'])

  # Architecture - armhf
  stats_build_filtered_debian = stats_build_mod[(stats_build_mod["name_y"] == "debian")]
  stats_build_filtered_debian_armhf = stats_build_filtered_debian[
    stats_build_filtered_debian["architecture"] == "armhf"]
  stats_build_filtered_debian_armhf = stats_build_filtered_debian_armhf[
    stats_build_filtered_debian_armhf["suite"] == 'unstable']
  stats_build_subset_debain_armhf = stats_build_filtered_debian_armhf[["id_x", "name_x", "status", "build_date"]]
  debian_tbl_sorted_armhf = stats_build_subset_debain_armhf.sort_values(by='build_date', ascending=False)
  debian_tbl_sorted_armhf['trim_date'] = pd.to_datetime(debian_tbl_sorted_armhf['build_date']).dt.date

  # Architecture - arm64
  stats_build_filtered_debian = stats_build_mod[(stats_build_mod["name_y"] == "debian")]
  stats_build_filtered_debian_arm64 = stats_build_filtered_debian[
    stats_build_filtered_debian["architecture"] == "arm64"]
  stats_build_filtered_debian_arm64 = stats_build_filtered_debian_arm64[
    stats_build_filtered_debian_arm64["suite"] == 'unstable']
  stats_build_subset_debain_arm64 = stats_build_filtered_debian_arm64[["id_x", "name_x", "status", "build_date"]]
  debian_tbl_sorted_arm64 = stats_build_subset_debain_arm64.sort_values(by='build_date', ascending=False)
  debian_tbl_sorted_arm64['trim_date'] = pd.to_datetime(debian_tbl_sorted_arm64['build_date']).dt.date

  armhf_packages = debian_tbl_sorted_armhf.name_x.unique().tolist()
  arm64_package = debian_tbl_sorted_arm64.name_x.unique().tolist()

  check_common_packages_in_armhf_and_arm64 = intersection(armhf_packages, arm64_package)
  print("Intersect of packages in armhf and arm64: " + str(len(check_common_packages_in_armhf_and_arm64)))

  armhf_packages = debian_tbl_sorted_armhf.groupby("name_x").first().reset_index()
  arm64_package = debian_tbl_sorted_arm64.groupby("name_x").first().reset_index()

  common_pkg_in_armhf = armhf_packages[armhf_packages.name_x.isin(check_common_packages_in_armhf_and_arm64)]
  common_pkg_in_armhf = common_pkg_in_armhf.rename(columns={'status': 'armhf_status'})

  common_pkg_in_arm64 = arm64_package[arm64_package.name_x.isin(check_common_packages_in_armhf_and_arm64)]
  common_pkg_in_arm64 = common_pkg_in_arm64.rename(columns={'status': 'arm64_status'})

  armhf_arm64_merge = pd.merge(common_pkg_in_armhf, common_pkg_in_arm64, on='name_x', validate='1:1')

  dataframe = armhf_arm64_merge[['name_x', 'armhf_status', 'arm64_status']]
  dataframe.loc[dataframe['armhf_status'] == 'reproducible', 'armhf_status'] = 1
  dataframe.loc[dataframe['armhf_status'] != 1, 'armhf_status'] = 0
  dataframe.loc[dataframe['arm64_status'] == 'reproducible', 'arm64_status'] = 1
  dataframe.loc[dataframe['arm64_status'] != 1, 'arm64_status'] = 0

  dataset_tbl = pd.crosstab(dataframe['armhf_status'], dataframe['arm64_status'])
  observed_values = dataset_tbl.values
  print("Observed Values :-\n", observed_values)

  stat, p, dof, expected = stats.chi2_contingency(dataset_tbl)
  print("Values of chi-quare statistics is: %f" % stat)
  print("p-value is: %f" % p)
  print("Effect size: \n", association(dataset_tbl, method="cramer"))

if __name__ == '__main__':
  main()