#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This module handles creation and authorisation of a set of data source adapters for
pulling engineering metrics.
"""
from dateutil.parser import parse
from datetime import datetime
import numpy as np
from typing import List, Dict

from configparser import ConfigParser
from jira import JIRA
import os


class FlowLog(list):
    """List subclass enforcing dictionaries with specific keys are added to it.

    A flow log is attached to each :py:class:`JiraIssue` in order to surface an issues journey
    through the workflow. Each entry in a flow log is a dictionary with the following keys:

        ``"entered_at"``
            When the ticket entered the state (datetime)
        ``"state"``
            The name of the state the ticket entered (string)
        ``"duration"``
            Time spent in this state (int)

    This should faciliate reporting on cycle time and should help to surface bottlenecks, by allowing
    issues to be graphed with regard to the time they spend in each ``"state"`` of a workflow.

    """

    def append(self, value: dict) -> None:
        """Add items to the list.

        Args:
            value (dict): Must contain an ``"entered_at"`` and ``"state key"``.

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


class JiraIssue(dict):
    """Representation of tickets from Jira.

    Attributes:
        issue (JIRA.issue): A Jira issue returned from a query
    """

    def __init__(self, issue: JIRA.issue) -> None:
        """Init a JiraIssue.

        Args:
            issue: A JIRA issue instance
        """
        # super(JiraIssue, self).__init__()
        try:
            self['ttype'] = issue.fields.issuetype.name
        except AttributeError:
            self['ttype'] = "Ticket"
        self._issue = issue

        self['id'] = issue.id
        self['key'] = issue.key
        self['url'] = issue.permalink()
        self['summary'] = issue.fields.summary
        self['labels'] = issue.fields.labels
        self['created'] = parse(issue.fields.created)
        self['updated_at'] = parse(issue.fields.updated)
        self['resolution'] = issue.fields.resolution
        self['resolutiondate'] = parse(
            issue.fields.resolutiondate) if issue.fields.resolutiondate else ''
        self['assignee'] = issue.fields.assignee
        self['description'] = issue.fields.description
        self['priority'] = issue.fields.priority.__str__().split(':')[0]
        self['status'] = issue.fields.status
        self['fixVersion'] = None
        if len(issue.fields.fixVersions) > 0:
            self["fixVersion"] = issue.fields.fixVersions[0]
        self['updated_at'] = None

        self._flow_log = FlowLog()
        self._flow_log.append(
            dict(
                entered_at=self['created'],
                state=str("Created")
            )
        )
        self['cycle_time'] = None
        self.cycle_time()
        try:
            previous_item = None
            for history in issue.changelog.histories:
                for item in history.items:
                    if item.field == 'status':
                        new_log_item = dict(
                            entered_at=parse(history.created),
                            state=str(item.toString)
                        )
                        if previous_item != None:
                            previous_item['duration'] = np.busday_count(  # pylint: disable=unsupported-assignment-operation
                                previous_item['entered_at'].date(), new_log_item['entered_at'].date())  # pylint: disable=unsupported-assignment-operation, unsubscriptable-object
                        previous_item = new_log_item
                        self._flow_log.append(new_log_item)
            if previous_item != None:
                previous_item['duration'] = np.busday_count(
                    previous_item['entered_at'].date(), datetime.now().date())
        except AttributeError:
            pass

    @property
    def flow_log(self) -> FlowLog:
        """
        :py:class:`FlowLog`: `flow_log`
            A list of dicts with the following keys:

            ``"entered_at"``
                When the ticket entered the state (datetime)
            ``"state"``
                The name of the state the ticket entered (string)
            ``"duration"``
                Time spent in this state (int)

        """
        return self._flow_log

    def cycle_time(self, resolution_status: str = None) -> int:
        """Counts the number of business days an issue took to resolve. This is
        the number of weekdays between the created data and the resolution date
        field on a ticket that is set to resolved. If no resolution date exists
        and the resolution_status paramter was passed the date a ticket entered the
        resolution status is used in place of resolution date.

        If both a resolution date found and resolution_status is set the resolution date
        is used. If neither a resolution date or resolution status are found -1 is returned.

        Args:
            resolution_status: A status to use in the case where no resolution date is set

        Returns:
            Number of days to resolve ticket or -1 if ticket is not resolved.
        """
        if self['cycle_time'] != None and self['cycle_time'] > -1:
            return self['cycle_time']
        self['cycle_time'] = -1

        if self['resolution']:
            if self['resolutiondate']:
                self['cycle_time'] = np.busday_count(
                    self['created'].date(), self['resolutiondate'].date())
            elif resolution_status:
                resolution_date = None
                for log in self._flow_log:
                    if log['state'] == resolution_status:
                        resolution_date = log['entered_at']
                if resolution_date != None:
                    self['cycle_time'] = np.busday_count(
                        self['created'].date(), resolution_date.date())

        self['cycle_time'] = self['cycle_time']
        return self['cycle_time']


class JQLResult(object):
    """This class wraps the results of a JQL query in order to provide some convenience methods.

    Args:
        query: The JQL query that produces the result set.
        label (optional): A string label used to cache the query result. If not set the default key
            `JQL` is used and the result overwrites any previous query results.
        issues: A list of :py:class:`JiraIssue` instances.

    """

    def __init__(self, query: str, label: str = 'JQL', issues: List[JiraIssue] = []) -> None:
        """Init a JQLResult

        Args:
            query: The JQL query that produces the result set.
            label (optional): A string label used to cache the query result. If not set the default key
                `JQL` is used and the result overwrites any previous query results.
            issues: A list of :py:class:`JiraIssue` instances.
        """
        self._query = query
        self._label = label
        self._issues = issues

    @property
    def query(self) -> str:
        """
        str: `query`
            The query that was run for this result set.
        """
        return self._query

    @property
    def label(self) -> str:
        """
        str: `label`
            A label for this query.
        """
        return self._label

    @property
    def issues(self) -> List[JiraIssue]:
        """
         List[:py:class:`JiraIssue`]: `issues`
            A list of :py:class:`JiraIssue` instances.
        """
        return self._issues

    def resolved_issues(self) -> List[JiraIssue]:
        """Return a list of just the issues that are understood to be resolved.

            Currently this is implemented by filtering a list of issues to only contain
            those with a cycle time greater that -1.

        Returns:
            List[JiraIssue]: A list of :py:class:`JiraIssue` instances considered to be resolved.

        """
        return list(filter(lambda d: d['cycle_time'] > -1, self._issues))


class JiraProject(JQLResult):
    """This subclass represents a project from Jira. It is really only a convenience class
        to wrap a JQL query that is intended to pull all issues from a project.

    """

    def __init__(self, project: JIRA.project, query_string: str = '') -> None:
        """Init a JiraProject

        Args:
            project (JiraProject): A JIRA project instance
            query_string (srt): The query used to grab this project data.
        """
        super().__init__(query_string, project.name, []) # The explicit [] avoids a caching issue
        self._key = project.key
        self._name = project.name

    @property
    def key(self) -> str:
        """
        str: `key`
            The project key as it is in Jira.
        """
        return self._key

    @property
    def name(self) -> str:
        """
        str: `name`
            The project name as it is in Jira.
        """
        return self._name


class Jira:
    """An Engineering Metrics wrapper for data we can harvest from Jira.
    """

    def __init__(self, jiraclient: JIRA) -> None:
        self._client = jiraclient
        self._datastore = {
            "issues": {},
            "projects": {}
        }

    def _getJiraIssuesForProjects(self, project_ids: List[str],  max_results: int = False) -> Dict[str, JiraProject]:

        issues_by_project = {}
        for pid in project_ids:
            #print(f'Request pdata for project id {pid}')
            pdata = self._client.project(pid)
            #print(f'pdata {pdata} received for project id {pid}')

            query_string = 'project = "{}" ORDER BY priority DESC'.format(pid)
            proj = JiraProject(pdata, query_string)
            print(f'{len(proj.issues)} existing issues for {pdata} project id {pid}')
            issues = self._client.search_issues(
                query_string,
                maxResults=max_results,
                expand='changelog'
            )
            print(f'{len(issues)} issues received for project id {pid}')
            for issue in issues:
                kt = JiraIssue(issue)
                proj.issues.append(kt)

            if len(proj.issues):
                issues_by_project[pid] = proj

        return issues_by_project

    def populate_projects(self, projectids: List[str], max_results: int = False) -> Dict[str, JiraProject]:
        """Populate the Jira instance with data from the Jira app.

        Given a list of ids this method will build a dictionary containing issues from
        each project in the list. As well as returning the data to the callee, this method
        stores the results internally to facilitate the use of a range of helper methods
        to analyse the data.

        Args:
            projectids: A list of project ids for which you want to pull issues.
            max_results: Limit the number of issues returned by the query.

        Returns:
            Dict[str, JiraProject]: A dictionary of JiraProjects. Each key will be the id for the corresponding project.
        """
        projects = self._getJiraIssuesForProjects(projectids,  max_results)
        self._datastore['projects'] = {
            **self._datastore['projects'], **projects}
        return projects

    def populate_from_jql(self, query: str = None, max_results: int = False, label: str = "JQL") -> JQLResult:
        """Populate the Jira instance with data from the Jira app accorging to a JQL
        string.

        Given a JQL string this method will build a dictionary containing issues returned
        by executing the query. As well as retuning the data to the callee, this method
        stores the results internally to facilitate the use of a range of helper methods
        to analyse the data.

        Args:
            query: The JQL query to perform against the Jira data.
            max_results: Limit the number of issues returned by the query.
            label (optional): A string label to store the query result internally. If not set the query
                result is stored under the key 'JQL' and overwrites any previous query results.

        Returns:
            JQLResult: an instance of :py:class:`JQLResult`
        """
        if query == None:
            raise ValueError("query string is required to get issues")

        result = self._client.search_issues(
            query, maxResults=max_results, expand='changelog')
        issues = list(map(lambda i: JiraIssue(i), result))
        query_result = JQLResult(query, label, issues)
        self._datastore[query_result.label] = query_result
        return query_result

    def get_query_result(self, label: str = 'JQL') -> Dict[str, object]:
        """Get a cached JQL query result dictionary

        Args:
            label (optional): The label supplied with the original query

        Returns:
            JQLResult: an instance of :py:class:`JQLResult`

        """
        return self._datastore[label]

    def get_project(self, pid: str) -> JiraProject:
        """Get a cached project for a given pid

        Args:
            pid: The project key assigned by Jira.

        Returns:
            JiraProject: A project.
        """
        try:
            project = self._datastore['projects'][pid]
            return project
        except KeyError:
            return KeyError(f'No project with key {pid} in the cache. Have you called Jira.populate_projects(["{pid}"])?')

    @property
    def jiraclient(self) -> JIRA:
        """
        JIRA: `jiraclient`
            The instance of `Jira's python client <https://jira.readthedocs.io/en/master/>`_ wrapped by this adapter.
        """
        return self._client

    @property
    def projects(self) -> Dict[str, JiraProject]:
        """
        Dict[str, JiraProject]: `projects`
            A dictionary of Jira Project instances by project key e.g. INT
        """
        return self._datastore['projects']


def init_jira_adapter(jira_oauth_config_path: str = None, jira_access_token: str = None) -> Jira:
    """Set up an adapter to pull data from Jira. Handles the auth flow and returns an instance of the Jira
    class that facilitates metircs analysis around Jira data.

    Args:
        jira_oauth_config_path:
            A string path to the oauth config setup. Used for Jira server.
        jira_access_token:
            The access token for Jira cloud (it's coming!)
    Returns:
        Jira: An instance of the Jira adapter class
    """
    if jira_oauth_config_path != None:
        path_to_config = os.path.join(jira_oauth_config_path,
                                      '.oauthconfig/.oauth_jira_config')
        #print(f'Reading OAuth from {path_to_config}')

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

        return Jira(JIRA(oauth=oauth_dict, server=jira_url))
