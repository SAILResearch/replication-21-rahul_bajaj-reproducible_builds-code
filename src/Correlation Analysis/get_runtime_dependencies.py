import pandas as pd
import subprocess
import networkx as nx
from io import StringIO
import warnings
warnings.filterwarnings("ignore")


def main():
  df = pd.read_csv("../../data/deb_direct_dependencies.csv")

  unique_dependencies = df.dependencies.unique().tolist()
  print("Build Dependencies: ", df.dependencies.nunique())

  edges_dict = dict()
  command = "debtree --with-suggests --max-depth 1 {}"
  for name in unique_dependencies:
    if name not in edges_dict.keys():
      try:
        process = subprocess.Popen(command.format(name).split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        if error is None:
          g = nx.drawing.nx_pydot.read_dot(StringIO(output.decode()))
          edges_dict[name] = list(g.edges())
        else:
          print(name, error)
      except:
        pass

  data = list()
  for name, edges in edges_dict.items():
    for node1, node2 in edges:
      data.append([name, node1, node2])

  df = pd.DataFrame(data, columns=["name", "package", "dependency"])

  # many packages have themselves as a dependency
  df = df[df["package"] != df["dependency"]]
  df.to_csv('transitive_dependency.csv', index=False)


if __name__ == '__main__':
  main()
