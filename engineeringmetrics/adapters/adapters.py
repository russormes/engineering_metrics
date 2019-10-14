#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Data Adapters
This module handles creation and authorisation of a set of data source adapters for
pulling engineering metrics.
"""
from dateutil.parser import parse
from datetime import datetime
from typing import List, Dict

from configparser import ConfigParser
from jira import JIRA
import os


class KarhooProject(dict):
    """Karhoo Ticket
    Representation of projects in Karhoo Jira.
    """

    def __init__(self, project: JIRA.project) -> None:
        """Init a KarhooProject

        Args:
            project: A JIRA project instance
        """
        self['key'] = project.key
        self['name'] = project.name
        self['issues'] = []


class KarhooTicket(dict):
    """Karhoo Ticket
    Representation of tickets in Karhoo Jira.

    Attributes:
        key (unicode): Unique identifier for the ticket in its system of record
        created_at (datetime): When was the ticket created
        updated_at (datetime): When was the ticket last updated
        type (str): The kind of ticket this is: Bug, Epic, Story, etc.

    Optional Attributes:
        title (unicode): The title of the ticket
    """

    def __init__(self, issue: JIRA.issue) -> None:
        """Init a KarhooTicket.

        Args:
            issue: A JIRA issue instance
        """
        # super(KarhooTicket, self).__init__()
        try:
            self['ttype'] = issue.fields.issuetype.name
        except AttributeError:
            self['ttype'] = "Ticket"
        self['id'] = issue.id
        self['key'] = issue.key
        self['url'] = issue.permalink()
        self['summary'] = issue.fields.summary
        self['labels'] = issue.fields.labels
        self['created'] = parse(issue.fields.created)
        self['updated_at'] = parse(issue.fields.updated)
        self['assignee'] = issue.fields.assignee
        self['description'] = issue.fields.description
        self['priority'] = issue.fields.priority.__str__().split(':')[0]
        self['status'] = issue.fields.status
        self['fixVersion'] = None
        if len(issue.fields.fixVersions) > 0:
            self["fixVersion"] = issue.fields.fixVersions[0]
        self['updated_at'] = None
        self['_flow_log'] = FlowLog()
        self['_flow_log'].append(
            dict(
                entered_at=self['created'],
                state=str("Created")
            )
        )

        try:
            for history in issue.changelog.histories:
                for item in history.items:
                    if item.field == 'status':
                        self['_flow_log'].append(
                            dict(
                                entered_at=parse(history.created),
                                state=str(item.toString)
                            )
                        )
        except AttributeError:
            pass

    @property
    def flow_log(self):
        """FlowLog[dict].

        A list of dicts guaranteed to have the following:
            entered_at (datetime): When the ticket entered the state
            state (unicode): The name of the state the ticket entered
        """
        return self['_flow_log']


class FlowLog(list):
    """List subclass enforcing dictionaries with specific keys are added to it."""

    def append(self, value):
        """Add items to the list.

        Args:
            value (dict): Must contain an entered_at and state key.

        Returns:
            None

        Raises:
            TypeError: Flow log items must have a 'entered_at' datetime and a 'state' string.
        """
        try:
            ('entered_at', 'state') in value.keys()
        except AttributeError:
            raise TypeError(
                "Flow log items must have a 'entered_at' datetime and a 'state' string. Got: {value}".format(value=value))

        entered_at = value['entered_at']
        try:
            datetime.now(entered_at.tzinfo) - entered_at
        except (AttributeError, TypeError) as e:
            msgvars = dict(
                val_type=type(entered_at),
                val=entered_at,
                exc=str(e)
            )
            raise TypeError(
                "Flow log items must have a entered_at datetime. Got: {val_type} / {val}, \n Exception: {exc}".format(**msgvars))

        value[u'state'] = str(value['state'])
        super(FlowLog, self).append(value)
        self.sort(key=lambda l: l['entered_at'])


class KJira:
    """An Engineering Metrics wrapper for data we can harvest from Jira

    Attributes:
        jiraclient (object): The instance of Jiras python client used to pul the data from metrics.
    """

    def __init__(self, jiraclient: JIRA) -> None:
        self._client = jiraclient
        self._datastore = {
            "issues": {},
            "projects": {}
        }

    def _getJiraIssuesForProjects(self, project_ids: List[str]) -> Dict[str, KarhooProject]:

        issues_by_project = {}
        for pid in project_ids:
            print(f'Request data for project id {pid}')
            pdata = self._client.project(pid)
            print(f'Data received for project id {pid}')

            proj = KarhooProject(pdata)
            print(f'Request issues for project id {pid}')
            issues = self._client.search_issues(
                'project = "{}" ORDER BY priority DESC'.format(pid),
                maxResults=False,
                expand='changelog'
            )
            print(f'Issues received for project id {pid}')
            # Does the query return the name?
            for issue in issues:
                kt = KarhooTicket(issue)
                proj['issues'].append(kt)

            if len(proj.get('issues')):
                issues_by_project[pid] = proj

        return issues_by_project

    def populateProjects(self, projectids: List[str]) -> Dict[str, Dict[str, object]]:
        """Populate the Karhoo Jira instance with data from the Jira app.

        Given a list of ids this method will build a dictionary containing issues from 
        each project in the list. As well as retuning the data to the callee, this method
        stores the results internally to facilitate the use of a range of helper methods
        to analyse the data.

        Args:
            projectids: A list of project ids for which you want to pull issues.

        Returns:
            A dictionary of KarhooProjects, Each key will be the project id which maps to 
            a KarhooProjects of the form
            {
                "name" (str): Project name
                "key"  (str): Project Key
                "issues" List[KarhooTickets]: A list of wrapped Jira issues
            }

        """
        projects = self._getJiraIssuesForProjects(projectids)
        self._datastore['projects'] = {
            **self._datastore['projects'], **projects}
        return projects

    def populateFromJQL(self, query: str = None, label: str = "JQL") -> Dict[str, object]:
        """Populate the Karhoo Jira instance with data from the Jira app accorging to a JQL
        string.

        Given a JQL string this method will build a dictionary containing issues returned 
        by executing the query. As weel as retuning the data to the callee, this method
        stores the results internally to facilitate the use of a range of helper methods
        to analyse the data.

        Args:
            query: The JQL query to perform against the Jira data.
            label (optional): A string label to store the quert result internally. If not set the query
                    reult is stored undert the key 'JQL' and overwrites any previous query results.

        Returns:
            a dictionary of the form
            {
                "name" (str): Set to the query string
                "key"  (str): Key used to store the result (set to label if provided or 'JQL' otherwise)
                "issues" List[KarhooTickets]: A list of wrapped Jira issues
            }

        """
        if query == None:
            raise ValueError("query string is required to get issues")

        result = self._client.search_issues(query,
                                            maxResults=False,
                                            expand='changelog'
                                            )
        issues = list(map(lambda i: KarhooTicket(i), result))
        return_dict = {
            "name": query,
            "key": label,
            "issues": issues
        }
        self._datastore[label] = return_dict
        return return_dict


def init_jira_adapter(jira_oauth_config_path: str = None, jira_access_token: str = None) -> KJira:
    if jira_oauth_config_path != None:
        path_to_config = os.path.join(jira_oauth_config_path,
                                      '.oauthconfig/.oauth_jira_config')
        print()

        print(
            f'Reading OAuth from {path_to_config}')

        config = ConfigParser()
        config.read(path_to_config)
        jira_url = config.get("server_info", "jira_base_url")
        oauth_token = config.get("oauth_token_config", "oauth_token")
        oauth_token_secret = config.get(
            "oauth_token_config", "oauth_token_secret")
        consumer_key = config.get("oauth_token_config", "consumer_key")

        rsa_private_key = None
        # Load RSA Private Key file.
        with open(os.path.join(jira_oauth_config_path, '.oauthconfig/oauth.pem'), 'r') as key_cert_file:
            rsa_private_key = key_cert_file.read()

        if jira_url[-1] == '/':
            jira_url = jira_url[0:-1]

        oauth_dict = {
            'access_token': oauth_token,
            'access_token_secret': oauth_token_secret,
            'consumer_key': consumer_key,
            'key_cert': rsa_private_key
        }

        return KJira(JIRA(oauth=oauth_dict, server=jira_url))
