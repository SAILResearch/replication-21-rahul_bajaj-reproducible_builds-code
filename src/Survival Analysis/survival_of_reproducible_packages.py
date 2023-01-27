import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt
from multiprocessing import Pool

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

  dataframes_list = [debian_unstable_df, debian_bookworm_df, debian_bullseye_df, debian_buster_df, debian_stretch_df,
                     debian_experimental_df, archlinux_community_df, archlinux_core_df, archlinux_extra_df,
                     archlinux_multilib_df]
  global base_df
  base_df = dataframes_list.copy()
  survival_of_reproducible_df = processing_reproducible_to_unreproducible(dataframes_list)

  # Perform Survival Analysis for Reproducible Packages at 30 and 360 days
  predict_deb_30 = []
  for df in survival_of_reproducible_df[0:6]:
    predict_deb_30.append(repro_survivalanalysis30(df))

  predict_deb_360 = []
  for df in survival_of_reproducible_df[0:6]:
    predict_deb_360.append(repro_survivalanalysis360(df))

  predict_arch_30 = []
  for df in survival_of_reproducible_df[6:]:
    predict_arch_30.append(repro_survivalanalysis30(df))

  predict_arch_360 = []
  for df in survival_of_reproducible_df[6:]:
    predict_arch_360.append(repro_survivalanalysis360(df))

  # Plot the diagram for Survival of Reproducible Packages in Debian and Arch Linux
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

def get_unreproducible_packages(package):
  package_name, trim_date = package
  date_time = []
  base_SurvivalAnalysis_status_zero_df = base_df[0][base_df[0].status_2 == 0]
  smaller_df = base_SurvivalAnalysis_status_zero_df[base_SurvivalAnalysis_status_zero_df.packages == package_name]
  for j in range(len(smaller_df)):
    if (smaller_df.iloc[j].trim_date > trim_date) & (smaller_df.iloc[j].status_2 == 0):
      date_time.append(smaller_df.iloc[j])
  return date_time


def processing_reproducible_to_unreproducible(dataframes_list):
  df_list = []
  for package_df in dataframes_list:
    # UnReproducible at first instance
    UnRepr_at1 = package_df[(package_df.status_2 == 0) & \
                            (package_df.rank_package_by_trimdate == 1)]
    UnRepr_afterFirstInstance = package_df[package_df['packages'].isin(UnRepr_at1.packages)]
    # Unreproducible to Reproducible after 1st instance (rank > 1)
    Repr_at2 = UnRepr_afterFirstInstance[
      (UnRepr_afterFirstInstance.status_2 == 1) & (UnRepr_afterFirstInstance.rank_package_by_trimdate > 1)]
    Repr_afterUnreproducible = Repr_at2.groupby(['packages'], as_index=False).trim_date.min()
    Repr_afterUnreproducible_list = list(Repr_afterUnreproducible.to_records(index=False))
    mp = Pool(processes=12)
    unrepr_packageAfterRepr = []
    unrepr_packageAfterRepr.append(mp.map(get_unreproducible_packages, Repr_afterUnreproducible_list))
    mp.terminate()
    flat_list = []
    for element in unrepr_packageAfterRepr:
      if type(element) is list:
        for item in element:
          flat_list.append(item)
      else:
        flat_list.append(element)
    unrepr_packageAfterRepr_df = pd.DataFrame([y for x in flat_list for y in x])
    unrepr_packageAfterRepr_df_firstInstance = unrepr_packageAfterRepr_df.groupby(['packages'],
                                                                                  as_index=False).trim_date.min()
    survival_of_Repro_df = Repr_afterUnreproducible.merge(unrepr_packageAfterRepr_df_firstInstance, on='packages',
                                                          how='left')
    survival_of_Repro_df.loc[survival_of_Repro_df['trim_date_y'].isnull() == True, 'event'] = 0
    survival_of_Repro_df.loc[survival_of_Repro_df['event'].isnull() == True, 'event'] = 1
    survival_of_Repro_df['trim_date_y'] = survival_of_Repro_df['trim_date_y'].replace(np.nan,
                                                                                      unrepr_packageAfterRepr_df.trim_date.max())
    survival_of_Repro_df['date_diff'] = pd.to_datetime(survival_of_Repro_df["trim_date_y"]) - pd.to_datetime(
      survival_of_Repro_df["trim_date_x"])
    survival_of_Repro_df['date_diff_days'] = survival_of_Repro_df['date_diff'].dt.days.astype(int)
    survival_of_Repro_df = survival_of_Repro_df[survival_of_Repro_df['date_diff_days'] <= 720]
    del base_df[0]
    df_list.append(survival_of_Repro_df)
  return df_list


def repro_survivalanalysis30(repro_df):
  kmf = KaplanMeierFitter()
  kmf.fit(repro_df['date_diff_days'],
          repro_df['event'],
          label='Unreproducible')
  return kmf.predict({30})


def repro_survivalanalysis360(repro_df):
  kmf = KaplanMeierFitter()
  kmf.fit(repro_df['date_diff_days'],
          repro_df['event'],
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
  plt.savefig("../../figures/repro-survival-scatter-plot.pdf", dpi=2000)
  plt.show()


if __name__ == '__main__':
  main()
