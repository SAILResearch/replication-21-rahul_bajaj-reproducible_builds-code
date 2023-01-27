import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")


def main():
  # Load databases
  distributions_tbl = pd.read_csv("../../data/distributions.csv", sep=",")
  stats_build = pd.read_csv("../../data/stats_build.csv", sep=',')

  stats_build_mod = pd.merge(stats_build, distributions_tbl, left_on="distribution", right_on="id")
  stats_build_mod = stats_build_mod.drop(columns=['distribution', 'id_y'])

  # Filter packages from all suites of Arch Linux and Debian
  debian_unstable_df = filter_packages(stats_build_mod, distribution="debian", architecture="amd64", suite="unstable")
  debian_bookworm_df = filter_packages(stats_build_mod, distribution="debian", architecture="amd64", suite="bookworm")
  debian_bullseye_df = filter_packages(stats_build_mod, distribution="debian", architecture="amd64", suite="bullseye")
  debian_buster_df = filter_packages(stats_build_mod, distribution="debian", architecture="amd64", suite="buster")
  debian_stretch_df = filter_packages(stats_build_mod, distribution="debian", architecture="amd64", suite="stretch")
  debian_experimental_df = filter_packages(stats_build_mod, distribution="debian", architecture="amd64", suite="experimental")
  archlinux_community_df = filter_packages(stats_build_mod, distribution="archlinux", architecture="x86_64", suite="community")
  archlinux_core_df = filter_packages(stats_build_mod, distribution="archlinux", architecture="x86_64", suite="core")
  archlinux_extra_df = filter_packages(stats_build_mod, distribution="archlinux", architecture="x86_64", suite="extra")
  archlinux_multilib_df = filter_packages(stats_build_mod, distribution="archlinux", architecture="x86_64", suite="multilib")

  # Calculate the time until event for unreproducible packages becoming reproducible
  suvival_of_unrpro_debian_unstable_df = processing_unreproducible_to_reproducible(debian_unstable_df)
  suvival_of_unrpro_debian_bookworm_df = processing_unreproducible_to_reproducible(debian_bookworm_df)
  suvival_of_unrpro_debian_bullseye_df = processing_unreproducible_to_reproducible(debian_bullseye_df)
  suvival_of_unrpro_debian_buster_df = processing_unreproducible_to_reproducible(debian_buster_df)
  suvival_of_unrpro_debian_stretch_df = processing_unreproducible_to_reproducible(debian_stretch_df)
  suvival_of_unrpro_debian_experimental_df = processing_unreproducible_to_reproducible(debian_experimental_df)
  survival_of_unrepro_archlinux_community_df = processing_unreproducible_to_reproducible(archlinux_community_df)
  survival_of_unrepro_archlinux_core_df = processing_unreproducible_to_reproducible(archlinux_core_df)
  survival_of_unrepro_archlinux_multilib_df = processing_unreproducible_to_reproducible(archlinux_multilib_df)
  survival_of_unrepro_archlinux_extra_df = processing_unreproducible_to_reproducible(archlinux_extra_df)

  survival_of_unreproducible_debian_df = [suvival_of_unrpro_debian_unstable_df, suvival_of_unrpro_debian_bookworm_df,
                                          suvival_of_unrpro_debian_bullseye_df, suvival_of_unrpro_debian_buster_df,
                                          suvival_of_unrpro_debian_stretch_df, suvival_of_unrpro_debian_experimental_df]
  survival_of_unreproducible_archlinux_df = [survival_of_unrepro_archlinux_community_df,
                                             survival_of_unrepro_archlinux_core_df,
                                             survival_of_unrepro_archlinux_multilib_df,
                                             survival_of_unrepro_archlinux_extra_df]

  # Perform Survival Analysis for Reproducible Packages at 30 and 360 days
  predict_deb_30 = []
  for df in survival_of_unreproducible_debian_df:
    predict_deb_30.append(unrepro_survivalanalysis30(df))

  predict_arch_30 = []
  for df in survival_of_unreproducible_archlinux_df:
    predict_arch_30.append(unrepro_survivalanalysis30(df))

  predict_deb_360 = []
  for df in survival_of_unreproducible_debian_df:
    predict_deb_360.append(unrepro_survivalanalysis360(df))

  predict_arch_360 = []
  for df in survival_of_unreproducible_archlinux_df:
    predict_arch_360.append(unrepro_survivalanalysis360(df))

  # Plot the diagram for Survival of Unreproducible Packages in Debian and Arch Linux
  plot_survival_graph(predict_deb_30, predict_deb_360, predict_arch_30, predict_arch_360)


def filter_packages(stats_build_mod, distribution, architecture, suite):
  stats_build_filtered = stats_build_mod[(stats_build_mod["name_y"] == distribution)]
  stats_build_filtered = stats_build_filtered[stats_build_filtered["architecture"] == architecture]
  stats_build_filtered = stats_build_filtered[stats_build_filtered["suite"] == suite]
  stats_build_sorted = stats_build_filtered.sort_values(by='build_date')
  stats_build_sorted['trim_date'] = pd.to_datetime(stats_build_sorted['build_date']).dt.date
  df1 = stats_build_sorted[["name_x", "status", "trim_date"]]
  df2 = df1.rename(columns={'name_x': 'packages'})
  df2.loc[df2['status'] == 'reproducible', 'status_2'] = 1
  df2.loc[df2['status_2'] != 1, 'status_2'] = 0
  # remove those packages that have the same data (trim date) and same status for the same package)
  df2_removedups = df2.drop_duplicates(subset=['packages', 'trim_date', 'status_2'])
  df2_removedups['rank_package_by_trimdate'] = df2_removedups.groupby('packages')['trim_date'].rank(ascending=True)
  return df2_removedups


def processing_unreproducible_to_reproducible(package_df):
  # UnReproducible at first instance
  UnRepr_at1 = package_df[(package_df.status_2 == 0) & (package_df.rank_package_by_trimdate == 1)]
  UnRepr_afterFirstInstance = package_df[package_df['packages'].isin(UnRepr_at1.packages)]
  # Unreproducible to Reproducible after 1st instance (rank > 1)
  Repr_at2 = UnRepr_afterFirstInstance[
    (UnRepr_afterFirstInstance.status_2 == 1) & (UnRepr_afterFirstInstance.rank_package_by_trimdate > 1)]
  Repr_afterUnreproducible = Repr_at2.groupby(['packages'], as_index=False).trim_date.min()
  survival_df = pd.merge(UnRepr_at1, Repr_afterUnreproducible, how='left', left_on='packages', right_on='packages')
  survival_df = survival_df.rename(columns={"trim_date_x": "Unreproducible_Date", "trim_date_y": "Reproducible_Date"})
  survival_df.loc[pd.isna(survival_df['Reproducible_Date']) == True, 'event'] = 0
  survival_df.loc[pd.isna(survival_df['event']) == True, 'event'] = 1
  survival_df['Reproducible_Date'] = survival_df['Reproducible_Date'].replace(np.nan, UnRepr_at1.trim_date.max())
  survival_df['date_diff'] = pd.to_datetime(survival_df.Reproducible_Date) - pd.to_datetime(
    survival_df.Unreproducible_Date)
  survival_df['date_diff_days'] = survival_df['date_diff'].dt.days.astype(int)
  survival_df = survival_df[survival_df.date_diff_days <= 720]
  return survival_df


def unrepro_survivalanalysis30(unrepro_df):
  kmf = KaplanMeierFitter()
  kmf.fit(unrepro_df['date_diff_days'],
          unrepro_df['event'],
          label='Unreproducible')
  return kmf.predict({30})


def unrepro_survivalanalysis360(unrepro_df):
  kmf = KaplanMeierFitter()
  kmf.fit(unrepro_df['date_diff_days'],
          unrepro_df['event'],
          label='Unreproducible')
  return kmf.predict({360})


def plot_survival_graph(predict_deb_30, predict_deb_360, predict_arch_30, predict_arch_360):
  plt.rcParams.update({'font.size': 14})
  plt.rcParams['axes.spines.right'] = False
  plt.rcParams['axes.spines.top'] = False
  plt.plot(range(1))

  x = predict_deb_30
  y = predict_deb_360
  plt.scatter(x, y, label='Debian Suites')

  x = predict_arch_30
  y = predict_arch_360
  plt.scatter(x, y, c='orange', label='Arch Linux Suites')

  plt.legend()
  plt.xlim(0, 1)
  plt.ylim(0, 1)
  plt.xlabel('Survival Probability at 30 days', fontsize=14)
  plt.ylabel('Survival Probability at 360 days', fontsize=14)
  plt.tight_layout()
  plt.savefig("../../figures/unrepro-survival-scatter-plot.pdf", dpi=2000)
  plt.show()


if __name__ == '__main__':
  main()
