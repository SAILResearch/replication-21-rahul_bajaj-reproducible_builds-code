# Replication package for Reproducible Builds study
Code in this repository corresponds to the `Unreproducible builds: Time to fix, causes, and
correlation with external ecosystem factors` paper submitted at the Empirical Software Engineering journal.

## Installation and execution
Data for this study is shared on [Dropbox](https://www.dropbox.com/s/n8tepo0hn21jfh6/data.zip?dl=0). Additionally, data is attached in the release notes. Unzip the file data.zip into the root of this repository.

```
# Create virtual envirement 
$ virtualenv env

# Activate virtual envirement
$ source env/bin/activate

# Install all packages required to run the analysis
$ pip install --editable .

# Running the script for analysis
$ python <script_name>
```

## Testing environment

Analyses conducted in this study have been tested on a system with 12 threads. You can check the number of threads in your system by using commands like `htop`. Update the number of threads for faster processing of [survival analysis](https://github.com/SAILResearch/wip-21-rahul_bajaj-reproducible_builds-code/blob/main/src/Survival%20Analysis/survival_of_reproducible_packages.py#L97)

