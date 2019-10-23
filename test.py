#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test
A script to run some local tests on the library
"""
from engineeringmetrics.engine import EngineeringMetrics
from pathlib import Path

config_dict = {
    'jira_oauth_config_path': Path.home()
}


def main():
    kem = EngineeringMetrics(config_dict)
    kem.jirametrics.populate_projects(['INT'])
    kem.jirametrics.populate_from_jql('project = "OSO" ORDER BY Rank ASC')

    print('yay')


if __name__ == '__main__':
    main()
