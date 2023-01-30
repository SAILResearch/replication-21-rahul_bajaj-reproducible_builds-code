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

  # Get Debian build data
  stats_build_filtered = stats_build_mod[(stats_build_mod["name_y"] == "debian")]
  stats_build_filtered = stats_build_filtered[stats_build_filtered["architecture"] == "amd64"]
  stats_build_filtered = stats_build_filtered[stats_build_filtered["suite"] == 'unstable']
  stats_build_sorted = stats_build_filtered.sort_values(by='build_date', ascending=False)
  stats_build_sorted['trim_date'] = pd.to_datetime(stats_build_sorted['build_date']).dt.date
  df = stats_build_sorted[["id_x", "name_x", "status", "trim_date"]]

  # Get Arch build data
  stats_build_filtered_archlinux = stats_build_mod[(stats_build_mod["name_y"] == "archlinux")]
  stats_build_filtered_archlinux = stats_build_filtered_archlinux[
    stats_build_filtered_archlinux["architecture"] == "x86_64"]
  stats_build_filtered_archlinux = stats_build_filtered_archlinux[
    stats_build_filtered_archlinux["suite"] == 'community']
  stats_build_sorted_archlinux = stats_build_filtered_archlinux.sort_values(by='build_date', ascending=False)
  stats_build_sorted_archlinux['trim_date'] = pd.to_datetime(stats_build_sorted_archlinux['build_date']).dt.date
  df1 = stats_build_sorted_archlinux[["id_x", "name_x", "status", "trim_date"]]

  debian_packages = df.name_x.unique().tolist()
  archlinux_package = df1.name_x.unique().tolist()

  check_common_packages_in_debian_and_archlinux = intersection(debian_packages, archlinux_package)
  print("Intersect of packages in debian and archlinux: " + str(len(check_common_packages_in_debian_and_archlinux)))

  debian_packages = df.groupby("name_x").first().reset_index()
  archlinux_packages = df1.groupby("name_x").first().reset_index()

  common_pkg_in_debian = debian_packages[debian_packages.name_x.isin(check_common_packages_in_debian_and_archlinux)]
  common_pkg_in_debian = common_pkg_in_debian.rename(columns={'status': 'debian status'})

  common_pkg_in_archlinux = archlinux_packages[
    archlinux_packages.name_x.isin(check_common_packages_in_debian_and_archlinux)]
  common_pkg_in_archlinux = common_pkg_in_archlinux.rename(columns={'status': 'arch status'})

  deb_arch_merge = pd.merge(common_pkg_in_debian, common_pkg_in_archlinux, on='name_x', validate='1:1')
  dataframe = deb_arch_merge[['name_x', 'debian status', 'arch status']]

  dataframe.loc[dataframe['debian status'] == 'reproducible', 'debian status'] = 1
  dataframe.loc[dataframe['debian status'] != 1, 'debian status'] = 0
  dataframe.loc[dataframe['arch status'] == 'reproducible', 'arch status'] = 1
  dataframe.loc[dataframe['arch status'] != 1, 'arch status'] = 0

  dataset_tbl = pd.crosstab(dataframe['debian status'], dataframe['arch status'])

  observed_values = dataset_tbl.values
  print("Observed Values :-\n", observed_values)

  stat, p, dof, expected = stats.chi2_contingency(dataset_tbl)
  print("Values of chi-quare statistics is: %f \n" % stat)
  print(f"p-value is: {p:.20f} \n")
  print("Effect size: \n", association(dataset_tbl, method="cramer"))


if __name__ == '__main__':
    main()
