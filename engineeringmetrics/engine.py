#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A library that provides a set of wrappers around data pulled from data sources from across the business"""

from typing import Dict, Mapping
from engineeringmetrics import adapters


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

    def __init__(self, config: Dict[str, str]) -> None:
        """Init a EngineeringMetrics.

        Args:
            config: A dictionary of config parameters.

                ``"jira_oauth_config_path"``
                    Path to the jira oauth config and keys (str)
                ``"jira_access_token"``
                    A valid access token for Jira cloud (str)
        """
        self._config: Dict[str, str] = config
        # A structure to store data source adapters for pulling in data to the metrics engine.
        self._data_adapters: Dict[str,
                                  object] = self._init_data_adapters(self._config)

    def _init_data_adapters(self, config: Dict[str, str]):

        data_adapters:  Dict[str, object] = {}

        if "jira_oauth_config_path" in config.keys():
            karhoojira = adapters.init_jira_adapter(
                config['jira_oauth_config_path'])
            data_adapters['jira'] = karhoojira

        return data_adapters

    @property
    def jirametrics(self) -> adapters.Jira:
        """
        Jira: `jirametrics`
            If Jira authentication is configured in the constructor this property
            is populated with an instance of the Jira adapter for pulling data from Jira.
        """
        return self._data_adapters['jira']
