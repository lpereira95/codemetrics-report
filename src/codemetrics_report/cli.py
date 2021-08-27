from pathlib import Path

import click

import codemetrics as cm
from codemetrics_report.report import gather_report_info
from codemetrics_report.report import create_html_report
from codemetrics_report.report import altair2json
from codemetrics_report.vis import create_loc_chart
from codemetrics_report.vis import create_age_chart
from codemetrics_report.vis import create_age_loc_chart
from codemetrics_report.vis import create_hotspots_chart


@click.command()
@click.argument('repo_path', nargs=1, type=str)
@click.option('--weeks', '-w', type=int, default=52)
def generate_codemetrics_report(repo_path, weeks):
    repo_path = convert_dirname_to_path(repo_path)
    project_name = repo_path.name

    # repo
    repo = cm.GitProject(repo_path)

    # get info
    loc, ages, hotspots = gather_report_info(repo)

    # create charts
    charts_json = {
        'loc': altair2json(create_loc_chart(loc)),
        'age': altair2json(create_age_chart(ages, weeks=weeks)),
        'loc_age': create_age_loc_chart(ages),
        'hotspots': create_hotspots_chart(hotspots)
    }

    filename = f'codemetrics_{project_name}.html'
    create_html_report(project_name, charts_json, filename=filename)


    print(f'\nCreated {filename}')


def convert_dirname_to_path(dir_name):
    """
    Notes:
        Handles definition of home with `~`.
    """
    dir_name_ls = dir_name.split('/')
    if dir_name_ls[0] == '~':
        path = Path.home() / '/'.join(dir_name_ls[1:])
    else:
        path = Path(dir_name)

    return path
