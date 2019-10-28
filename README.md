# Karhoo Engineering Metrics
A python lib to pull out some engineering metrics from various data sources such as issue tracking software and event logs.

## Getting Started

### Docs

I don't currently have a solution for hosting the doc pages. Instead you will need to view them locally. To do this, clone the repo, build the docs and view in your favorite browser (or one you don't like but have installed).

```sh
# Requires python 3.6. Get you virtual env out.
pip install -r requirements.docs.txt
cd docs/
make html
```

The docs are written to the sub directory `_build/html` and can be viewied from the `index.html` page.

```sh
# e.g. On mac
open  "_build/html/index.html"
```

### Jira Cloud api token

Auth is a much easier game with Jira cloud. You simply need an api token. Get one [here](https://id.atlassian.com/manage/api-tokens) and then use it to initiate the Engineering Metrics lib.

```python
from engineeringmetrics import EngineeringMetrics

config_dict = {
    'jira_username': '<YourJira@CloudUsername>',
    'jira_api_token': 'YourbP0APIkavuKeyQ72C4',
    'jira_server_url': 'https://karhoo.atlassian.net'
}
kem = EngineeringMetrics(config_dict)
```

### oAuth for Jira Server
Until we hit the cloud you will need to generate some access tokens to use this library against the Jira Server instance we have. This can be done using the script found in the `token_generator` directory. Follow the [README](./token_generator/README.md) down the rabbit hole.
