import pickle
import requests
import pandas as pd


def send_request(pkg_version):
  packages_with_404_response = []
  pkg_dep_dict = {}
  for key, value in pkg_version.items():
    res = requests.get(
      "https://sources.debian.org/data/main/{initial}/{pkg_name}/{pkg_version}/debian/control".format(initial=key[0],
                                                                                                      pkg_name=key,
                                                                                                      pkg_version=value))
    if res.status_code == 200:
      text_data = res.text.split('\n')
      filter_object = filter(lambda a: 'Build-Depends' in a, text_data)
      try:
        dependencies = list(filter_object)[0].split(':')[1]
        stripped_list = []
        for value in dependencies.split():
          stripped_list.append(value.rstrip(','))
        depends = []
        for value in stripped_list:
          if (value[0] == '(') or (value[-1] == ')') or ('(' in value) or (')' in value):
            continue
          else:
            depends.append(value)
        pkg_dep_dict[key] = depends
      except:
        pass
    else:
      packages_with_404_response.append(key)
      continue
  return pkg_dep_dict


def main():
  # Load databases
  pkg_version_data = open("data.pkl", "rb")
  pkg_version = pickle.load(pkg_version_data)
  pkg_dep_dict = send_request(pkg_version)

  df = pd.DataFrame([(key, var) for (key, L) in pkg_dep_dict.items() for var in L],
                 columns=['packages', 'dependencies'])
  df.to_csv('debian_dependency_graph_tbl.csv', index=False)


if __name__ == '__main__':
  main()