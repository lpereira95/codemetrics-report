`codemetrics-report` builds on top of [`codemetrics`](https://pypi.org/project/codemetrics/) to quickly generate an `html` report of a repo.


The generated `html` report contains interactive graphs with:

* lines of code for each programming language
* age of files and recent development activity
* lines of code and file age
* hotspots


Check out this [blog post](https://cerfacs.fr/coop/codemetrics) for a hands-on introduction to `codemetrics`. Most of the code in which the report relies on is based on this [notebook](https://github.com/elmotec/codemetrics/blob/master/notebooks/pandas.ipynb).


Many thanks to Eloi Démolis for the development of the main methods present in the `html` template and Jérôme Lecomte for the development of `codemetrics`.


## Usage

The following command creates an `html` file in your current working directory (simply open it with your favorite web browser):

```bash
generate-codemetrics-report <repo_location>
```


## Installation

```bash
pip install codemetrics-report
```