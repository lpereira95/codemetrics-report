import os
import re
import json
import datetime as dt

import codemetrics as cm
from tqdm import tqdm
import pandas as pd


def gather_report_info(repo, after=None):
    # TODO: better to develop a class for this
    if after is None:
        after = dt.datetime.now(tz=dt.timezone.utc) - dt.timedelta(365 * 50)

    # long info
    log = repo.get_log(after=after)

    # loc info
    loc_all = cm.get_cloc(repo)
    idx_vcs = loc_all.path.isin(log.path.unique())  # keep only under vcs
    idx_vcs.iloc[-1] = True  # keep sum
    loc = loc_all[idx_vcs].reset_index()

    # ages
    ages = cm.get_ages(log).merge(loc)

    # complexity
    tqdm.pandas(desc="computing complexity")
    complexity = (log[['path', 'date']]
                  .groupby(['path'], as_index=False)
                  .max()
                  .merge(log[['path', 'date', 'revision']])
                  .groupby(['revision', 'path'])
                  .progress_apply(cm.get_complexity, project=repo))
    path_complexity = (complexity
                       .reset_index()[['path', 'cyclomatic_complexity', 'token_count']]
                       .groupby('path').quantile(0.8)
                       .sort_values(by='cyclomatic_complexity', ascending=False)
                       .reset_index()
                       .rename(columns={'cyclomatic_complexity': 'complexity'})
                       )
    loc_cc = pd.merge(loc, path_complexity)
    hotspots = cm.get_hot_spots(log, loc_cc)

    return loc, ages, hotspots


def create_html_report(project_name, charts_json,
                       filename='codemetrics_report.html'):
    """
    Args:
        charts_json (dict): JSON data.
            Must contain: 'loc', 'age', 'loc_age', 'hotspots'.
    """

    # read template
    template_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     'codemetrics_template.html')
    with open(template_filename, 'r') as file:
        template = file.read()

    # add json data
    html = template
    for plot_name, chart_data in charts_json.items():
        search_str = r'\{\{' + plot_name + r'\}\}'
        html = re.sub(search_str, json.dumps(chart_data),
                      html)

    # add project name
    html = re.sub(r'\{\{project_name\}\}', project_name, html)

    # create html file
    with open(filename, 'w') as file:
        file.write(html)


def create_html_report_from_files(project_name, charts_dir,
                                  filename='codemetrics_report.html'):

    # read json
    charts_json = {}
    for plot_name in ['loc', 'age', 'loc_age', 'hotspots']:
        chart_filename = os.path.join(charts_dir, plot_name)

        with open(f'{chart_filename}.json', 'r') as file:
            charts_json[plot_name] = json.load(file)

    return create_html_report(project_name, charts_json, filename=filename)


def altair2json(chart):
    return json.loads(chart.to_json())
