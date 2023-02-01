import urllib.request
from html_table_parser.parser import HTMLTableParser
import pandas as pd
import warnings
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")


def url_get_contents(url):
  req = urllib.request.Request(url=url)
  f = urllib.request.urlopen(req)
  return f.read()


def is_package_affected(rq2_mod):
  issue_packages_list = rq2_mod[['issue_name', 'concencus_list', 'affected_packages']]
  affected_package_summary = issue_packages_list.affected_packages.value_counts().to_frame()
  affected_package_summary.affected_packages.mean()
  affected_package_summary.affected_packages.describe()
  affected_package_summary = affected_package_summary[affected_package_summary.affected_packages < 89]


  plt.rcParams.update({'font.size': 6})
  fig, axes = plt.subplots(figsize=(2, 2))
  g = axes.violinplot(affected_package_summary["affected_packages"], showmeans=False, showmedians=False,
                      showextrema=False)
  for pc in g['bodies']:
    pc.set_facecolor('orange')
    pc.set_edgecolor('black')
    pc.set_alpha(1)
  axes.set_xlabel('Affected Packages')
  axes.set_ylabel('Number of Root Causes')
  axes.spines['right'].set_visible(False)
  axes.spines['top'].set_visible(False)

  plt.tight_layout()
  plt.tick_params(labelbottom=False, bottom=False)
  plt.savefig("../../figures/affected_packages.pdf", dpi=2000)
  plt.show()


def main():
  xhtml = url_get_contents('https://tests.reproducible-builds.org/debian/index_issues.html').decode('utf-8')

  # Defining the HTMLTableParser object
  p = HTMLTableParser()
  p.feed(xhtml)

  # Create dataframe from the data obtained
  df = pd.DataFrame(p.tables[0])

  issues_tbl = pd.read_csv('../../data/manual_issues_classification.csv')
  issues_tbl_filtered = issues_tbl[['Issue Identifier', 'Consensus']]
  issues_tbl_filtered = issues_tbl_filtered.drop_duplicates(subset=['Issue Identifier'])
  issues_tbl_filtered = issues_tbl_filtered.rename(columns={'Issue Identifier': 'issue_name'})

  df.columns = df.iloc[0]
  df1 = df.iloc[1:, :]
  df2 = df1[['Identified issues', 'Number of packages',
             'Affected packages (the 1/4 most-popular ones (within the issue) are underlined)']]
  df3 = df2.rename(columns={'Identified issues': 'issue_name', 'Number of packages': "no_of_package",
                            'Affected packages (the 1/4 most-popular ones (within the issue) are underlined)': "affected_packages"})
  final_df = issues_tbl_filtered.merge(df3, how='inner', on='issue_name')

  final_df['concencus_list'] = final_df["Consensus"].str.split(',')
  rq2_mod = final_df.explode('concencus_list')
  rq2_mod['concencus_list'] = rq2_mod['concencus_list'].str.strip()

  rq2_mod['affected_packages'] = rq2_mod['affected_packages'].str.split(',')
  rq2_mod = rq2_mod.explode('affected_packages')
  rq2_mod['affected_packages'] = rq2_mod['affected_packages'].str.strip()
  issue_packages_list = rq2_mod[['issue_name', 'concencus_list', 'affected_packages']]

  #issue_packages_list.to_csv('rq2_final_with_all_concensus_and_affected_packages.csv', index=False)
  rq2_file = pd.read_csv('../../data/rq2_final_with_all_concensus_and_affected_packages.csv')
  rq2_file['concencus_list'] = rq2_file["Consensus"].str.split(',')
  rq2_mod = rq2_file.explode('concencus_list')
  rq2_mod['concencus_list'] = rq2_mod['concencus_list'].str.strip()

  # Number of issue affecting each root cause
  print("Number of issues for each root cause: \n")
  rq2_mod_2 = rq2_mod[['issue_name', 'concencus_list']]
  rq2_mod_2 = rq2_mod_2.drop_duplicates()
  print(rq2_mod_2.concencus_list.value_counts())

  # Affected packages from each root cause
  print("Number of packages affected by each root cause: \n")
  rq2_mod_3 = rq2_mod[['concencus_list', 'affected_packages']]
  rq2_mod_3 = rq2_mod_3.drop_duplicates()
  print(rq2_mod_3.concencus_list.value_counts())

  is_package_affected(rq2_mod)

if __name__ == '__main__':
  main()