import json
import jinja2
import logging
import os
from google.oauth2 import service_account

from arg_parser import fetch_input_args
from py_github_helper.utils.commands import (
    get_files_changed_during_pr,
    add_comment
)


# Path to this directory
dbt_table_diff_dir = os.path.dirname(os.path.abspath(__file__))

# Useful strings for f-string formatting Logs
new_line = "  \n"
bullet = f"{new_line}- "
break_line = f"{new_line}---{new_line}{new_line}"
indented_new_line = "  \n\t"
indented_bullet = f"{indented_new_line}- "


def get_pandas(project_id, keyfile_path):
    """
    Initializes pandas package to leverage GCP credentials.

    :param project_id: The unique id of your GCP Project.
    :param keyfile_path: The local path to your GCP keyfile.
    :return: Pandas library, with GCP credentials configured.
    """
    import pandas
    import pandas_gbq
    credentials = service_account.Credentials.from_service_account_file(
        keyfile_path,
    )
    pandas_gbq.context.credentials = credentials
    pandas_gbq.context.project = project_id
    return pandas


def get_relevant_files(files):
    """
    Filters on files matching the pattern "models/(.+)+.sql"

    :param files: A list of files (ie. files modified in branch or PR)
    :return: A list of SQL files in any sub-folder of models/
    """
    relevant_files = []
    for file in files:
        if file.startswith("models/") and file.endswith(".sql"):
            relevant_files.append(file)
    return relevant_files


def parse_manifest(manifest_file, files, ignored_schemas, dev_prefix):
    """
    Parses manifest_file for models which have an 'original_file_path' matching one of the files.

    :param manifest_file: The target/manifest.json file created from 'dbt compile'
    :param files: A list of files (ie. files modified in branch or PR)
    :param ignored_schemas: Schemas to ignore (ie. their models only exist in dev)
    :param dev_prefix: Prefix of the schema (when target=dev)
    :return: A list of models (db, schema, table)
    """
    models = []
    with open(manifest_file) as file:
        run_results = json.loads(file.read())
        for file in files:
            for model_id, model_details in run_results["nodes"].items():
                if model_details["original_file_path"] == file:
                    if model_details["schema"].startswith(dev_prefix) and model_details["schema"] not in ignored_schemas:
                        database = model_details["database"]
                        schema = model_details["schema"]
                        table = model_details["name"]
                        models.append([database, schema, table])
    return models


def run_checks(pd, project_id, models, sql_checks_path, dev_prefix, prod_prefix, fallback_prefix, irregular_schemas):
    """
    Loops over files in sql_checks_path and runs each of the checks for each model in models.

    :param models: List of tables to run checks on
    :param sql_checks_path: Path to folder containing sql checks to run
    :param dev_prefix: Prefix of dev schema
    :param prod_prefix: Prefix of prod schema
    :param fallback_prefix: One-off prefix for irregular_schemas
    :param irregular_schemas: List of schemas that dont use prod_prefix in production
    :return: Dictionary containing all SQL results
        Format: '{sql_check: {table: [dev_schema, prod_schema, results]}}'
    """
    results = {}
    if os.path.exists(sql_checks_path):
        logging.error(f"Running checks in path: {sql_checks_path}.")
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(sql_checks_path))
        for file in os.listdir(sql_checks_path):
            template = env.get_template(file)
            results[file] = {}
            for database, schema, table in models:
                logging.info(f"File: {file}, Schema: {schema}, Table: {table}")
                if schema in irregular_schemas:
                    compare_schema = schema.replace(dev_prefix, fallback_prefix)
                else:
                    compare_schema = schema.replace(dev_prefix, prod_prefix)
                sql = template.render(dataset=project_id, table=table, schema=schema,
                                      compare_schema=compare_schema)
                data = pd.read_gbq(sql)
                if not data.empty:
                    logging.info(sql)
                    values = data.values.tolist()
                    logging.info(f"Results: {values}")
                    results[file][table] = (schema, compare_schema, values)
            if len(results[file]) == 0:
                results.pop(file)
    else:
        logging.error(f"File path '{sql_checks_path}' not found.")
    return results


def parse_results(results):
    """
    Iterates over SQL check results formats them into a readable format.

    :param results: (dict) Contains output from all sql checks for all models
    :return: (str) comment in Markdown format
    """
    output = f"**Failures:**{bullet}{bullet.join(results.keys())}"

    for sql_check, tables in results.items():
        if sql_check == "check_table_row_count.sql":
            output += f"{new_line}{new_line}**Test:** {sql_check}"
            output += f"{new_line}| Table Name | Dev Count | Prod Count | Diff % |"
            output += f"{new_line}| --- | --- | --- | --- |"
            tables = {k: v for k, v in
                sorted(
                    tables.items(),
                    key=lambda item: item[1][2][0][3],
                    reverse=True
                )
            }
            for table_name, table_details in tables.items():
                if table_details:
                    dev, prod, rows = table_details
                    for row in rows:
                        tn = str(table_name)
                        r0 = str(row[0])
                        r1 = str(row[1])
                        r3 = str('{:.2f}'.format(row[3] * 100))
                        output += f"{new_line}| {tn} | {r0} | {r1} | {r3}% |"
        elif sql_check == "check_table_column_count.sql":
            output += f"{new_line}{new_line}**Test:** {sql_check}"
            for table_name, table_details in tables.items():
                only_prod = []
                only_dev = []
                if table_details:
                    dev, prod, rows = table_details
                    output += f"{bullet}{prod}.{table_name}"
                    for row in rows:
                        if row[0] == "Column only found in Dev":
                            only_dev.append(row[1])
                        elif row[0] == "Column only found in Prod":
                            only_prod.append(row[1])
                if only_dev:
                    output += f"{indented_bullet}Columns only found in {dev}: {','.join(only_dev)}"
                if only_prod:
                    output += f"{indented_bullet}Columns only found in {prod}: {','.join(only_prod)}"
        else:
            output += f"{new_line}{new_line}**Custom Test:** {sql_check}"
            for table_name, table_details in tables.items():
                if table_details:
                    dev, prod, rows = table_details
                    output += f"{bullet}{prod}.{table_name}"
                    for row in rows:
                        output += f"{indented_bullet}Results: {','.join(str(val) for val in row)}"
    return output

def build_comment(formatted_results, files):
    formatted_comment = f"{break_line}**Relevant Files Changed:**{new_line}"
    if files:
        formatted_comment += indented_bullet + indented_bullet.join(files)
    formatted_comment += break_line
    if formatted_results:
        formatted_comment += formatted_results
    else:
        formatted_comment += "**No Results to show**"
    return formatted_comment


def run_dbt_table_diff(
        project_id,
        keyfile_path,
        manifest_file,
        dev_prefix,
        prod_prefix,
        fallback_prefix,
        custom_checks_path,
        ignored_schemas,
        irregular_schemas,
        org_name,
        repo_name,
        pr_id,
        auth_token
):

    # Configure Pandas for specific BigQuery Project
    pd = get_pandas(project_id=project_id, keyfile_path=keyfile_path)

    # Get files changed during Pull Request
    files = get_files_changed_during_pr(
        organization=org_name,
        repository=repo_name,
        pull_request_id=pr_id,
        token=auth_token,
    )

    # Filter modified file on SQL files in models/
    logging.error(f"Files Changed:{new_line + new_line.join(files)}")
    relevant_files = get_relevant_files(files)
    logging.error(f"Relevant Files:{new_line + new_line.join(relevant_files)}")

    # Parse manifest.json for relevant models (modified SQL files in models/)
    models = parse_manifest(
        manifest_file=manifest_file,
        files=relevant_files,
        ignored_schemas=ignored_schemas,
        dev_prefix=dev_prefix
    )
    tables = [table for db, schema, table in models]
    logging.error(f"Relevant Models:{new_line + new_line.join(tables)}")
    print(' '.join(relevant_files))
    # Run SQL Checks, if files in models/*.sql were updated
    if models:
        standard_results = run_checks(
            pd=pd,
            project_id=project_id,
            models=models,
            sql_checks_path=os.path.join(dbt_table_diff_dir, "sql_checks/"),
            dev_prefix=dev_prefix,
            prod_prefix=prod_prefix,
            fallback_prefix=fallback_prefix,
            irregular_schemas=irregular_schemas)
        custom_results = run_checks(
            pd=pd,
            project_id=project_id,
            models=models,
            sql_checks_path=custom_checks_path,
            dev_prefix=dev_prefix,
            prod_prefix=prod_prefix,
            fallback_prefix=fallback_prefix,
            irregular_schemas=irregular_schemas
        )
        results = {**standard_results, **custom_results}

        # Add Comment to the Pull Request
        # # Parse SQL Check results dictionary into a markdown output file
        if results:
            formatted_check_results = parse_results(results)
            formatted_comment = build_comment(files=relevant_files, formatted_results=formatted_check_results)
            add_comment(
                organization=org_name,
                repository=repo_name,
                pull_request_id=pr_id,
                message=formatted_comment,
                token=auth_token,
                username=None,
                password=None,
            )


def parse_flags_and_run():
    # Parse CLI Flags
    input_args = fetch_input_args()
    manifest_file = input_args.manifest_file
    project_id = input_args.project_id
    keyfile_path = input_args.keyfile_path
    dev_prefix = input_args.dev_prefix
    prod_prefix = input_args.prod_prefix
    fallback_prefix = input_args.fallback_prefix
    custom_checks_path = ""
    if input_args.custom_checks_path:
        custom_checks_path = input_args.custom_checks_path
    ignored_schemas = []
    if input_args.ignored_schemas:
        ignored_schemas = input_args.ignored_schemas.split(",")
    irregular_schemas = []
    if input_args.irregular_schemas:
        irregular_schemas = input_args.irregular_schemas.split(",")
    org_name = input_args.org_name
    repo_name = input_args.repo_name
    pr_id = input_args.pr_id
    auth_token = input_args.auth_token

    run_dbt_table_diff(
        project_id,
        keyfile_path,
        manifest_file,
        dev_prefix,
        prod_prefix,
        fallback_prefix,
        custom_checks_path,
        ignored_schemas,
        irregular_schemas,
        org_name,
        repo_name,
        pr_id,
        auth_token
    )


if __name__ == "__main__":
    parse_flags_and_run()
