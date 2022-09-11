# dbt_table_diff
  
This repository is intended for comparing `BigQuery`  `models` in `dbt` that have changed during an open PR.   
  
[![PyPI version](https://badge.fury.io/py/dbt_table_diff.svg)](https://pypi.org/project/dbt_table_diff/)
[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/org-not-included/dbt_table_diff/main)](https://www.codefactor.io/repository/github/org-not-included/dbt_table_diff)
[![GitHub license](https://img.shields.io/github/license/org-not-included/dbt_table_diff)](https://github.com/org-not-included/dbt_table_diff/blob/main/LICENSE)  
[![GitHub pull requests](https://img.shields.io/github/issues-pr/org-not-included/dbt_table_diff)](https://github.com/org-not-included/dbt_table_diff/pulls)
[![GitHub issues](https://img.shields.io/github/issues/org-not-included/dbt_table_diff)](https://github.com/org-not-included/dbt_table_diff/issues)
[![GitHub contributors](https://img.shields.io/github/contributors/org-not-included/dbt_table_diff)](https://github.com/org-not-included/dbt_table_diff/graphs/contributors)  
[![GitHub Release Date](https://img.shields.io/github/release-date/org-not-included/dbt_table_diff)](https://github.com/org-not-included/dbt_table_diff/releases)
[![GitHub last commit](https://img.shields.io/github/last-commit/org-not-included/dbt_table_diff)](https://github.com/org-not-included/dbt_table_diff/commits/main)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/org-not-included/dbt_table_diff)](https://github.com/org-not-included/dbt_table_diff/graphs/commit-activity)  
[![GitHub forks](https://img.shields.io/github/forks/org-not-included/dbt_table_diff)](https://github.com/org-not-included/dbt_table_diff/network)
[![GitHub stars](https://img.shields.io/github/stars/org-not-included/dbt_table_diff)](https://github.com/org-not-included/dbt_table_diff/stargazers)
[![GitHub watchers](https://img.shields.io/github/watchers/org-not-included/dbt_table_diff)](https://github.com/org-not-included/dbt_table_diff/watchers)
[![Twitter Follow](https://img.shields.io/twitter/follow/OrgNotIncluded?style=flat)](https://twitter.com/intent/follow?screen_name=OrgNotIncluded)  
---  
  
## Usage
The repository has been published as a `Github Action` and `PyPi Package`, which means it can be leveraged in a variety of ways:  
- [Directly in Python](#example-code-usage) via `run_dbt_table_diff`.
- [Directly in Terminal](#example-cli-usage) via `python3 -m dbt_table_diff`.
- [In a Github Workflow File](https://github.com/org-not-included/dbt_example/blob/main/.github/workflows/main.yml) via `Github Actions` to [automatically add comments](https://github.com/org-not-included/dbt_example/pull/2) on Open PRs.
  
---
## Quick Start:

```text
pip3 install dbt_table_diff
```

---
<a name="example_code_usage"></a>
### Example Code Usage:
```text
from dbt_table_diff import run_dbt_table_diff

run_dbt_table_diff(
        project_id="ultimate-bit-359101",
        keyfile_path="secrets/bq_keyfile.json",
        manifest_file="target/manifest.json",
        dev_prefix="dev_",
        prod_prefix="prod_",
        fallback_prefix="fb_",
        custom_checks_path="",
        ignored_schemas=[],
        irregular_schemas=[],
        org_name="org-not-included",
        repo_name="dbt_example",
        pr_id="2",
        auth_token="my_github_pat",
)
```
  
---
  
<a name="example_cli_usage"></a>
### Example CLI Usage:
```shell
python3 -m dbt_table_diff -t $GH_TOKEN -o org-not-included -r dbt_example -l 2 \
--manifest_file 'target/manifest.json' --project_id 'ultimate-bit-359101' \
--keyfile_path 'secrets/bq_keyfile.json' --dev_prefix 'dev_' --prod_prefix 'prod_' --fallback_prefix 'fb_'
```
  
---
  
<a name="example_github_action"></a>
### Example Github Action Usage:  
- [Overview](https://docs.github.com/en/actions/quickstart) of Github Actions
- [Open PR](https://github.com/org-not-included/dbt_example/pull/2) showing how to use `dbt_table_diff` as a Github Action.
  
---
  
#### Github Actions Input Arguments:
  
| Input Parameter    | Description                                                                                                                                                                                   |  
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| GCP_TOKEN          | for connecting to BQ (runs `dbt compile` and `dbt_table_diff/sql_checks` to compare tables)                                                                                                   |  
| GH_TOKEN           | for connecting to Github (ie. fetches modified `models/*.sql` in your PR, adds comment on your PR)                                                                                            |  
| PR_NUMBER          | for fetching open PR from github (Pull Request ID \[int\])                                                                                                                                    |  
| GH_REPO            | for fetching open PR from github (Repository Name)                                                                                                                                            |  
| GH_ORG             | for fetching open PR from github (Repository owner/organization name)                                                                                                                         |  
| DBT_PROFILE_FILE   | the local path in your repo to your `profile.yml` for dbt (this is necessary for compiling `manifest.json` during setup process)                                                              |  
| dev_prefix         | the prefix used when running dbt locally (Your source schema/environment for comparison)                                                                                                      |  
| prod_prefix        | the prefix used when running dbt remotely (Your target schema/environment for comparison)                                                                                                     |  
| fallback_prefix    | useful if you have an overriden macro for `generate_schema_name` in your dbt project, which leverages a different prefix for some schemas in prod.                                            |  
| irregular_schemas  | comma separated string of schemas which use `fallback_prefix`                                                                                                                                 |  
| project_id         | for connecting to BQ (BigQuery Project ID)                                                                                                                                                    |
| ignored_schemas    | comma separated string of schemas to ignore (skip checking during github action)                                                                                                              |  
| custom_checks_path | [A local folder](https://github.com/org-not-included/dbt_example/pull/2/files#diff-f4d51a7463db0554f7d182b594d436ce0594a635756f477df1e9ab5768b3cf13) containing any custom SQL checks to run. |  
  
---  
  
## Step-By-Step Break Down of Process:  
  
- Fetches list of files modified in Pull Request
  - by CURLing `github.api.com/repos/{organization}/{repository}/pulls/{pull_request_id}/files`
- Filters on `relevant_files`
  - which are files matching `models/*.sql`
- Builds `manifest.json`
  - By running `dbt deps; dbt compile`
- Parses `manifest.json` for `relevant_models`
  - using manifest-attribute `original_file_path` matching `relevant_files`
- Runs all SQL files in `dbt_table_diff/sql_checks`
  - for each of the `relevant_models`, compare the two dbt targets (`dev_prefix` vs `prod_prefix`)
- Saves output to file
  - in a format supported by Github comments
- Posts comment on open PR
  - leveraging `dbt_table_diff` PyPi package
  
---  
  
## Docs
```shell
python3 -m dbt_table_diff --help
```
  
---
  
```text
usage: dbt_table_diff [-h] [-o ORG_NAME] [-r REPO_NAME] [-t AUTH_TOKEN] [-l PR_ID] [--manifest_file MANIFEST_FILE] [--project_id PROJECT_ID] [--keyfile_path KEYFILE_PATH] [--ignored_schemas IGNORED_SCHEMAS]
                      [--irregular_schemas IRREGULAR_SCHEMAS] [--dev_prefix DEV_PREFIX] [--prod_prefix PROD_PREFIX] [--fallback_prefix FALLBACK_PREFIX] [--custom_checks_path CUSTOM_CHECKS_PATH]

optional arguments:
  -h, --help            show this help message and exit
  -o ORG_NAME, --org_name ORG_NAME
                        Owner of GitHub repository.
  -r REPO_NAME, --repo_name REPO_NAME
                        Name of the GitHub repository.
  -t AUTH_TOKEN, --auth_token AUTH_TOKEN
                        User's GitHub Personal Access Token.
  -l PR_ID, --pr_id PR_ID
                        The issue # of the Pull Request.
  --manifest_file MANIFEST_FILE
                        The path to dbt's manifest file.
  --project_id PROJECT_ID
                        The BigQuery Project ID to leverage.
  --keyfile_path KEYFILE_PATH
                        The path to the keyfile to use during BQ calls.
  --ignored_schemas IGNORED_SCHEMAS
                        Folders in models/ to always ignore during row/col checks.
  --irregular_schemas IRREGULAR_SCHEMAS
                        Folders in models/ which use 'fallback_prefix' in prod.
  --dev_prefix DEV_PREFIX
                        Prefix used by development datasets in dbt.
  --prod_prefix PROD_PREFIX
                        Prefix used by production datasets in dbt.
  --fallback_prefix FALLBACK_PREFIX
                        Uncommon prefix used by only some production datasets in dbt.
  --custom_checks_path CUSTOM_CHECKS_PATH
                        A local folder containing any custom SQL to run.
```
