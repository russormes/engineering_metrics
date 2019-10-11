#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Engineering Metrics"""

from typing import Dict, Mapping
from .adapters import adapters


class EngineeringMetrics:
    """Entry point to Engineering Metrics."""

    def __init__(self, config: Dict[str, str]) -> None:
        """Init a EngineeringMetrics.

        Args:
            config: A dictionary of config parameters.
                jira_oauth_config_path (str): Path to the jira oauth config and keys
                jira_access_token (str): A valid access token for Jira cloud
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
    def jirametrics(self) -> adapters.KJira:
        """JiraMetrics[obj].

        An engineering metrics adapter for using Jira as a data source.
        """
        return self._data_adapters['jira']
