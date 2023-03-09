# fireproxify

[![Release](https://img.shields.io/github/v/release/y0k4i-1337/fireproxify)](https://img.shields.io/github/v/release/y0k4i-1337/fireproxify)
[![Build status](https://img.shields.io/github/actions/workflow/status/y0k4i-1337/fireproxify/main.yml?branch=main)](https://github.com/y0k4i-1337/fireproxify/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/y0k4i-1337/fireproxify/branch/main/graph/badge.svg)](https://codecov.io/gh/y0k4i-1337/fireproxify)
[![Commit activity](https://img.shields.io/github/commit-activity/m/y0k4i-1337/fireproxify)](https://img.shields.io/github/commit-activity/m/y0k4i-1337/fireproxify)
[![License](https://img.shields.io/github/license/y0k4i-1337/fireproxify)](https://img.shields.io/github/license/y0k4i-1337/fireproxify)

Fireprox as a package

- **Github repository**: <https://github.com/y0k4i-1337/fireproxify/>
- **Documentation** <https://y0k4i-1337.github.io/fireproxify/>

## Quick start

You can install `fireproxify` from PyPI with:

```
pip install fireproxify
```

or

```
pipx install fireproxify
```

## Usage

```
fire -h                               
usage: fire [-h] [--profile_name PROFILE_NAME] [--access_key ACCESS_KEY] [--secret_access_key SECRET_ACCESS_KEY] [--session_token SESSION_TOKEN]
            [--region REGION] [--command COMMAND] [--api_id API_ID] [--url URL]

FireProx API Gateway Manager

options:
  -h, --help            show this help message and exit
  --profile_name PROFILE_NAME
                        AWS Profile Name to store/retrieve credentials
  --access_key ACCESS_KEY
                        AWS Access Key
  --secret_access_key SECRET_ACCESS_KEY
                        AWS Secret Access Key
  --session_token SESSION_TOKEN
                        AWS Session Token
  --region REGION       AWS Regions (accepts single region, comma-separated list of regions or file containing regions)
  --command COMMAND     Commands: list, list_all, create, delete, prune, update
  --api_id API_ID       API ID
  --url URL             URL end-point
```

## Documentation in progress

While the documentation for package is not ready, please see [Documentation for Fireprox](https://github.com/y0k4i-1337/fireprox).
