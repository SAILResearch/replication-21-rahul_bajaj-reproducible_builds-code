# Replication package for Reproducible Builds study
Code in this repository corresponds to the `Unreproducible builds: Time to fix, causes, and
correlation with external ecosystem factors` paper submitted to the Empirical Software Engineering journal (EMSE). 

The `src` folder contains code for survival analysis, manual labeling and correlation analysis that correspond to the three research questions explored in the paper. We use the Python programming language to perform the aforementioned analysis. Once the source code is executed, figures generated during execution will be stored in the `figures` folder.  

## Abstract

**Context** A reproducible build occurs if, given the same source code, build instructions, and dependencies, compiling a software project repeatedly generates the same build artifacts. Reproducible builds are essential to identify tampering attempts responsible for supply chain attacks, with most of the research on reproducible builds considering build reproducibility as a project-specific issue. In contrast, modern software projects are part of a larger ecosystem and depend on dozens of other projects, which begs the question of to what extent build reproducibility of a project is the responsibility of that project or perhaps something forced on it. 

**Objective** This empirical study aims at analyzing reproducible and unreproducible builds in Linux Distributions to systematically investigate the process of making builds reproducible in open-source distributions. Our study targets build performed on 11,528 and 597,066 Arch Linux and Debian packages, respectively. 

**Method**  We compute the likelihood of unreproducible packages becoming reproducible (and vice versa) and identify the root causes behind unreproducible builds. Finally, we compute the correlation between the reproducibility status of packages and four ecosystem factors (i.e., factors outside the control of a given package). 

**Results** Arch Linux packages become reproducible a median of 92 days quicker when compared to Debian packages, while Debian packages remain reproducible for a median of 44 days longer once fixed. We identified 16 root causes of unreproducible builds. The build reproducibility status of a package across different hardware architectures is statistically significantly different (strong effect size). At the same time, the status also differs between versions of a package for different distributions and is based on the build reproducibility of a package's build dependencies, albeit with weaker effect sizes. 

**Conclusions** The ecosystem project belongs to, plays an important role w.r.t. the project’s build reproducibility. Since these are outside a developer's control, future work on (fixing) unreproducible builds should consider these ecosystem agents.

## Installation and execution

**Data** Data for this study is shared on [Dropbox](https://www.dropbox.com/s/n8tepo0hn21jfh6/data.zip?dl=0). Please place the data folder obtained from dropbox into the root of this repository. Additionally, data is attached in the release notes. Unzip the file data.zip into the root of this repository.

This code has been tested to run on Fedora 35 with Python 3.10 version. However, this program must run on any operating system with Python > 3.0 version.

```
# Create virtual environment 
$ virtualenv env

# Activate virtual environment
$ source env/bin/activate

# Install all packages required to run the analysis
$ pip3 install --editable .

# Running the script for analysis
$ python3 <script_name>
```

## Notes

**Survival Analysis**: Analyses conducted in this study have been tested on a system with 12 threads. You can check the number of threads in your system by using commands like `htop`. Update the number of threads for faster processing of [survival analysis](https://github.com/SAILResearch/wip-21-rahul_bajaj-reproducible_builds-code/blob/main/src/Survival%20Analysis/survival_of_reproducible_packages.py#L97)

**Correlation Analysis**:
1. The program `get_build_dependencies.py` will generate a new file in the `data` folder, namely `debian_dependency_graph_tbl_new.csv`. The data in this file is scraped from the Debian packages [website](https://sources.debian.org/data/main/). The new file generated may output different build dependencies, and therefore we use the `debian_dependency_graph_tbl.csv` file, in `build_dependencies.py`,  which was run at the time of performing the experiment.

2. The program `get_runtime_dependencies.py` needs to be run in a Debian 11 machine. During the time of the experiment, we use a [Vagrant machine](https://developer.hashicorp.com/vagrant/docs/installation) to create the same. Paste and run the program `get_runtime_dependencies.py` in a Debian 11 vagrant machine to obtain the `transitive_dependencies.csv` file as given in the data folder.

## Co-authors

Rahul Bajaj  
Eduardo Fernandes  
Bram Adams  
Ahmed E. Hassan
