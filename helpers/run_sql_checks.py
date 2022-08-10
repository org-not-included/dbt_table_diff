import json
import logging
import os

import jinja2
import pandas
import pandas_gbq
from google.oauth2 import service_account

from arg_parser import fetch_input_args


def get_pandas(project_id, keyfile_path):
    """
    Initializes pandas package to leverage GCP credentials.
    Returns:
        pandas library, with GCP credentials configured.
    """
    credentials = service_account.Credentials.from_service_account_file(
        keyfile_path,
    )
    pandas_gbq.context.credentials = credentials
    pandas_gbq.context.project = project_id
    return pandas

def get_relevant_files(files):
    relevant_files = []
    for file in files:
        if file.startswith("models/") and file.endswith(".sql"):
            relevant_files.append(file)
    return relevant_files


def parse_manifest(manifest_file, files, ignored_schemas, dev_prefix):
    # ========================================================================
    # Fetch Models for target/manifest.json
    # ========================================================================
    models = []
    schemas = set()
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
                        schemas.add(schema)
    return models, schemas


def run_checks(models, sql_checks_path, dev_prefix, prod_prefix, fallback_prefix, irregular_schemas):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(sql_checks_path))
    for file in os.listdir(sql_checks_path):
        template = env.get_template(file)
        results[file] = {}
        for database, schema, table in models:
            logging.info(f"File: {file}, Schema: {schema}, Table: {table}")
            pd = get_pandas(project_id=project_id, keyfile_path=keyfile_path)
            if schema in irregular_schemas:
                compare_schema = schema.replace(dev_prefix, fallback_prefix)
            else:
                compare_schema = schema.replace(dev_prefix, prod_prefix)
            sql = template.render(dataset=project_id, table=table, schema=schema, compare_schema=compare_schema)
            data = pd.read_gbq(sql)
            if not data.empty:
                logging.info(sql)
                values = data.values.tolist()
                logging.info(f"Results: {values}")
                results[file][table] = (schema, compare_schema, values)
        if len(results[file]) == 0:
            results.pop(file)
    return results


def save_results(results, output_file):
    # ========================================================================
    # Fetch Test Results from BigQuery and Print them cleanly
    # ========================================================================
    output = f"**Failures:**{bullet}{bullet.join(results.keys())}"

    for sql_check, tables in results.items():
        if sql_check == "check_table_row_count.sql":
            output += f"{new_line}{new_line}**Test:** {sql_check}"
            output += f"{new_line}| Table Name | Dev Count | Prod Count | Diff % |"
            output += f"{new_line}| --- | --- | --- | --- |"
            tables = {k: v for k, v in sorted(tables.items(), key=lambda item: item[1][2][0][3], reverse=True)}
            for table_name, table_details in tables.items():
                if table_details:
                    dev, prod, rows = table_details
                    for row in rows:
                        tn = str(table_name)
                        r0 = str(row[0])
                        r1 = str(row[1])
                        r3 = str('{:.2f}'.format(row[3]*100))
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

    with open(output_file, "w+") as file:
        file.write(output)


if __name__ == "__main__":

    files, input_args = fetch_input_args()
    manifest_file = input_args.manifest_file
    project_id = input_args.project_id
    keyfile_path = input_args.keyfile_path
    ignored_schemas = input_args.ignored_schemas.split(",")
    irregular_schemas = input_args.irregular_schemas.split(",")
    dev_prefix = input_args.dev_prefix
    prod_prefix = input_args.prod_prefix
    fallback_prefix = input_args.fallback_prefix
    output_file = input_args.output_file

    pd = get_pandas(project_id=project_id, keyfile_path=keyfile_path)

    new_line = "  \\n"
    bullet = f"{new_line}- "
    indented_new_line = "  \\n\\t"
    indented_bullet = f"{indented_new_line}- "

    logging.error(f"Files Changed:{new_line + new_line.join(files)}")
    relevant_files = get_relevant_files(files)
    logging.error(f"Relevant Files:{new_line + new_line.join(relevant_files)}")
    models, schemas = parse_manifest(manifest_file=manifest_file, files=relevant_files, ignored_schemas=ignored_schemas, dev_prefix=dev_prefix)
    tables = [table for db, schema, table in models]
    logging.error(f"Relevant Models:{new_line + new_line.join(tables)}")
    if models:
        results = run_checks(models=models, sql_checks_path="helpers/sql_checks", dev_prefix=dev_prefix, prod_prefix=prod_prefix, fallback_prefix=fallback_prefix, irregular_schemas=irregular_schemas)
        if results:
            save_results(results, output_file)
    print(' '.join(relevant_files))
