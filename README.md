**Description:**
This github action is intended for comparing `models` that have changed in an open PR.

**Overview of process:**
- Fetches modified files by CURLing `github.api.com/repos/{organization}/{repository}/pulls/{pull_request_id}/files`
- Filters on files matching `models/*.sql` (call these `relevant_files`)
- Runs `dbt deps; dbt compile` to build `manifest.json`
- Parses `manifest.json` and fetches `relevant_models` with manifest-attribute `original_file_path` in `relevant_files`
- Loops over `models`
  - Runs all SQL files in `helpers/sql_checks` for each of the `relevant_models` (comparing `dev vs prod` via (dev_prefix` and `prod_prefix`)
  - Saves output to file, in pretty format for github comment
  - Leverages `py-github-helper` to post comment on open PR

**Github Actions Input Arguments:**
Look at [this working example](https://github.com/org-not-included/dbt_example/blob/5ff89b5d059b7c8b101bd08744bd9d01342bfb77/.github/workflows/main.yml), if you are unfamiliar with `Github Actions Inputs`. `Inputs` are used to configure Github Actions, and can be thought of as parameters/config, so the action knows what to do.

**How inputs are used:**
- `GCP_TOKEN` -> for connecting to BQ
   -  runs `dbt compile` and `helpers/sql_checks` to compare tables
- `GH_TOKEN` -> for connecting to Github
   - fetches modified `models/*.sql` in your PR
   - adds comment on your PR
- `PR_NUMBER` -> for fetching open PR from github (the PR your running this action against)
- `GH_REPO` -> for fetching open PR from github (the PR your running this action against)
- `GH_ORG` -> for fetching open PR from github (the PR your running this action against)
- `dev_prefix` -> the prefix used when running dbt locally (aka your dev environment)
- `prod_prefix` -> the prefix used when running dbt remotely (aka your prod environment)
- `fallback_prefix` -> if you have a custom `generate_schema_name`, where you have a different prefix **for some models in prod,** you can set this field to that prefix
- `project_id` -> for connecting to BQ (the BQ project id)
- `DBT_PROFILE_FILE` -> the local path in your repo to your `profile.yml` for dbt 
   - this is necessary for compiling `manifest.json` during setup process
- `ignored_schemas` -> comma separated string of schemas to ignore (skip checking during github action)
- `irregular_schemas` -> comma separated string of schemas which use `fallback_prefix` (described above)


**Quick Start:**
A bare-bones example can be found [here](https://github.com/org-not-included/dbt_example/pull/2).
![Screen Shot 2022-08-11 at 3 42 04 PM](https://user-images.githubusercontent.com/101577043/184239324-9384b0d2-0d32-4a17-8b5b-41b59b78038e.png)

