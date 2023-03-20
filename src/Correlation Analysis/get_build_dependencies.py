import pickle
import requests
import pandas as pd
from multiprocessing import Pool


def send_request(pkg_version):
  key, value = pkg_version

  # get all build dependencies for each package in the unstable suite of Debian
  if key[:3] == 'lib':
    res = requests.get(
      "https://sources.debian.org/data/main/{initial}/{pkg_name}/{pkg_version}/debian/control".format(initial=key[:4],
                                                                                                      pkg_name=key,
                                                                                                      pkg_version=value))
  else:
    res = requests.get(
      "https://sources.debian.org/data/main/{initial}/{pkg_name}/{pkg_version}/debian/control".format(initial=key[0],
                                                                                                      pkg_name=key,
                                                                                                      pkg_version=value))

  # filter the text response to get the dependencies
  if res.status_code == 200:
    tmp = res.content.decode("utf-8")
    try:
      tmp = tmp[tmp.index('Build-Depends'):]
      dependencies = tmp.split(':')[1].split(',\n')
      last_item = dependencies.pop()
      dependencies.append(last_item.split('\n')[0])
    except:
      return (key, [])

    converted_list = []
    for element in dependencies:
      converted_list.append(element.strip())

    split_list = []
    for value in converted_list:
      split_list.append(value.split(' '))
    flat_list = [item for sublist in split_list for item in sublist]

    stripped_list = []
    for value in flat_list:
      stripped_list.append(value.rstrip(','))

    depends = []
    if not stripped_list:
      return (key, depends)
    else:
      for value in stripped_list:
        if ('(' in value) or (')' in value) or ('<!' in value) or ('>' in value) or ('|' in value):
          pass
        else:
          depends.append(value)
    return (key, depends)
  else:
    return (key, [])


def main():
  # Load databases
  pkg_version_data = open("../../data/data.pkl", "rb")
  pkg_version = pickle.load(pkg_version_data)
  pkg_ver = list(pkg_version.items())

  p = Pool(12)
  pkg_dep_dict = dict(p.map(send_request, pkg_ver))

  df = pd.DataFrame([(key, var) for (key, L) in pkg_dep_dict.items() for var in L],
                    columns=['packages', 'dependencies'])
  df.to_csv('../../data/debian_dependency_graph_tbl_new.csv', index=False)


if __name__ == '__main__':
  main()
