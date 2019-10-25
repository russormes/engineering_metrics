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

### oAuth for Jira Server
Until we hit the cloud you will need to generate some access tokens to use this library against the Jira Server instance we have. This can be done using the script found in the `token_generator` directory. Follow the [README](./token_generator/README.md) down the rabbit hole.
