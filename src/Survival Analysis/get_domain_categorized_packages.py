import requests
from bs4 import BeautifulSoup
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


def main():
  # List of all the domains available.
  categorized_packages = []
  package_type = ["admin", "cli-mono", "comm", "debian-installer", "debug", "devel", "doc", "editors", "education",
                  "electronics", "embedded", "fonts", "games", "gnome", "gnu-r", "gnustep", "golang", "graphics",
                  "hamradio", "haskell", "httpd", "interpreters", "introspection", "java", "javascript", "kde",
                  "kernel", "libdevel", "libs", "lisp", "localization", "mail", "math", "metapackages", "misc", "net",
                  "news", "ocaml", "oldlibs", "otherosfs", "perl", "php", "python", "ruby", "rust", "science", "shells",
                  "sound", "tasks", "tex", "text", "utils", "vcs", "video", "virtual", "web", "x11", "xfce", "zope"]

  for domain in package_type:
    res = requests.get("https://packages.debian.org/sid/{package_type}/".format(package_type=domain))
    if res.status_code == 200:
      soup = BeautifulSoup(res.content, 'html.parser')
      a_tags = soup.select('dt a')
      packages = []
      for s in a_tags:
        packages.append(s['href'].strip())
      package_df = pd.DataFrame()
      package_df = pd.DataFrame(packages, columns=["packages"])
      package_df["type"] = domain
      categorized_packages.append(package_df)

  categorized_packages_df = pd.concat(categorized_packages)
  categorized_packages_drop_dups_df = categorized_packages_df.drop_duplicates(subset=['packages', 'type'])
  print("Categorized Packages: \n")
  print(categorized_packages_drop_dups_df.shape)


if __name__ == '__main__':
  main()
