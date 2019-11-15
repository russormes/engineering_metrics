#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A library that provides a set of wrappers around data pulled from data sources from across the business"""

from engineeringmetrics import adapters
from operator import itemgetter
from pathlib import Path
from typing import Dict, Mapping

CONFIG_KEYS = ['jira_api_token', 'jira_username',
               'jira_server_url', 'jira_oauth_config_path']


class EngineeringMetrics:
    """Entry point to Engineering Metrics.

    The class accepts a configuration map in its constructor and 
    uses that to configure a set of clients for pulling data from various
    sources.

    config is a dict with the following keys:

        ``"jira_oauth_config_path"``
            Path to the jira oauth config and keys (str)
        ``"jira_access_token"``
            A valid access token for Jira cloud (str)

    Example usage:

        To create an instance of the engineeringmetrics.EngineeringMetrics class:

            >>> from engineeringmetrics import EngineeringMetrics
            >>> from pathlib import Path
            >>> config_dict = {
                    'jira_oauth_config_path': Path.home()
                }
            >>> em = EngineeringMetrics(config_dict)

    """

    def __init__(self, config: Dict[str, str] = None) -> None:
        """Init a EngineeringMetrics.

        Args:
            config: A dictionary of config parameters.

                ``"jira_oauth_config_path"``
                    Path to the jira oauth config and keys (str)
                ``"jira_access_token"``
                    A valid access token for Jira cloud (str)
        """
        if not config:
            config = {'jira_oauth_config_path': Path.home()}

        self._config: Dict[str, str] = self.___set_config___(config)
        # A structure to store data source adapters for pulling in data to the metrics engine.
        self._data_adapters: Dict[str,
                                  object] = self._init_data_adapters(self._config)

    def ___set_config___(self, config_param, config_keys=CONFIG_KEYS):
        conf = config_param.copy()
        for k in config_keys:
            conf.setdefault(k, None)
        return conf

    def _init_data_adapters(self, config: Dict[str, str]):

        data_adapters:  Dict[str, object] = {}

        jira_api_token, jira_username, jira_server_url, jira_oauth_config_path = itemgetter(
            'jira_api_token', 'jira_username', 'jira_server_url', 'jira_oauth_config_path')(config)

        if jira_api_token and jira_username and jira_server_url:
            jira_adapter = adapters.init_jira_adapter(
                jira_api_token=jira_api_token, jira_username=jira_username, jira_server_url=jira_server_url)
            data_adapters['jira'] = jira_adapter
        elif jira_oauth_config_path != None:
            jira_adapter = adapters.init_jira_adapter(
                jira_oauth_config_path=jira_oauth_config_path)
            data_adapters['jira'] = jira_adapter

        return data_adapters

    @property
    def jirametrics(self) -> adapters.Jira:
        """
        Jira: `jirametrics`
            If Jira authentication is configured in the constructor this property
            is populated with an instance of the Jira adapter for pulling data from Jira.
        """
        return self._data_adapters['jira']


def jirametrics(config: Dict[str, str] = None) -> adapters.Jira:
    """Factory function for returning instances of the jira adapter

    Args:
        config: A dictionary of config parameters.

            ``"jira_oauth_config_path"``
                Path to the jira oauth config and keys (str)
            ``"jira_api_token"``
                A valid access token for Jira cloud (str)
            ``"jira_username"``
                The username for jira cloud instance (str)
            ``"jira_server_url"``
                The url of your jira cloud instance (str)

    Returns:
        adapters.Jira: An instance of :py:class:`adapters.Jira`

    """
    config_dict = {
        'jira_oauth_config_path': Path.home()
    }
    return EngineeringMetrics(config_dict).jirametrics
