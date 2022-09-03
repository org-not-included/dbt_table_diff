---

### Description:

This `Github Action` is intended for comparing `models` in `dbt` that have changed during an open PR.  
It only currently supports `BigQuery`.

---

### Step-By-Step Break Down of Process:  
  
- Fetches list of files modified in Pull Request
  - by CURLing `github.api.com/repos/{organization}/{repository}/pulls/{pull_request_id}/files`
- Filters on `relevant_files`
  - which are files matching `models/*.sql`
- Builds `manifest.json`
  - By running `dbt deps; dbt compile`
- Parses `manifest.json` for `relevant_models`
  - using manifest-attribute `original_file_path` matching `relevant_files`
- Runs all SQL files in `helpers/sql_checks`
  - for each of the `relevant_models`, compare the two dbt targets (`dev_prefix` vs `prod_prefix`)
- Saves output to file
  - in a format supported by Github comments
- Posts comment on open PR
  - leveraging `py-github-helper` PyPi package

---  

### Github Actions Input Arguments:

---  

### Quick Start:

[This example Workflow File](https://github.com/org-not-included/dbt_example/blob/main/.github/workflows/main.yml) shows how to configure the Github Action via `Github Actions Inputs`.  
[This example Pull Request](https://github.com/org-not-included/dbt_example/pull/2) shows the output of the Github Action.  
![Screen Shot 2022-08-11 at 3 42 04 PM](https://user-images.githubusercontent.com/101577043/184239324-9384b0d2-0d32-4a17-8b5b-41b59b78038e.png)

---

### How inputs are used:
  
  
| Input Parameter             | Description                                                                                                                                        |  
|-----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| GCP_TOKEN                   | for connecting to BQ (runs `dbt compile` and `helpers/sql_checks` to compare tables)                                                               |  
| GH_TOKEN                    | for connecting to Github (ie. fetches modified `models/*.sql` in your PR, adds comment on your PR)                                                 |  
| PR_NUMBER                   | for fetching open PR from github (Pull Request ID \[int\])                                                                                         |  
| GH_REPO                     | for fetching open PR from github (Repository Name)                                                                                                 |  
| GH_ORG                      | for fetching open PR from github (Repository owner/organization name)                                                                              |  
| DBT_PROFILE_FILE            | the local path in your repo to your `profile.yml` for dbt (this is necessary for compiling `manifest.json` during setup process)                   |  
| dev_prefix                  | the prefix used when running dbt locally (Your source schema/environment for comparison)                                                           |  
| prod_prefix                 | the prefix used when running dbt remotely (Your target schema/environment for comparison)                                                          |  
| fallback_prefix             | useful if you have an overriden macro for `generate_schema_name` in your dbt project, which leverages a different prefix for some schemas in prod. |  
| irregular_schemas           | comma separated string of schemas which use `fallback_prefix`                                                                                      |  
| project_id                  | for connecting to BQ (BigQuery Project ID)                                                                                                         |
| ignored_schemas             | comma separated string of schemas to ignore (skip checking during github action)                                                                   |  
  