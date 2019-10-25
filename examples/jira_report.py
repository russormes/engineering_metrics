#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Example script to print out a markdown report
"""
from engineeringmetrics import EngineeringMetrics
from pathlib import Path
import os

config_dict = {
    'jira_oauth_config_path': Path.home()
}


def pPriority(priority):
    """Parse status in to P1 - P4 and add some emotion!"""

    s = ''
    if priority == 'Blocker':
        s += "P1 🚨😫😭"
    elif priority == 'Highest':
        s += "P2 😭😭"
    elif priority == 'High':
        s += "P3 😟"
    elif priority == "Normal":
        s += "P4 🤔"
    return s


def createMarkdownReport(project):
    s = "# Known Issues Report\n"
    s += "Generated automatically from JIRA\n"
    s += '\n'
    s += "## {} Known Issues\n".format(project.name)
    for issue in project.issues:
        url = issue['url']
        s += "#### {} ([{}]({})) {}\n".format(issue['key'],
                                              issue['summary'], url, pPriority(issue['priority']))
        # s += pPriority(issue['priority'])
        s += "* JIRA: [{}]({})\n".format(url, url)
        s += "* Status: {}\n".format(issue['status'])
        if issue['fixVersion']:
            s += "* Fix: This was fixed in version {}\n".format(
                issue['fixVersion'])
        s += '\n'
    return s


SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
MARKDOWN_FILE = f'{SCRIPT_PATH}/report.md'


def main():
    kem = EngineeringMetrics(config_dict)
    project_list = kem.jirametrics.populate_projects(['INT'], max_results=20)
    md = createMarkdownReport(project_list['INT'])
    with open(MARKDOWN_FILE, 'w', encoding='utf-8') as f:
        f.write(md)

    print('yay, we did it!')


if __name__ == '__main__':
    main()
