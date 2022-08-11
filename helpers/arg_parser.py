import argparse
import ast

def format_args(input_args):
    """
    Transform user input args from strings to their actual types.
    """
    files = ast.literal_eval(input_args.files)
    return files, input_args

def fetch_input_args():
    """
    Parse user input args from the command line into variables.
    """
    parser = argparse.ArgumentParser("simple_example")
    parser.add_argument(
        "--files", help="List of modified .sql files in models/."
    )
    parser.add_argument(
        "--manifest_file", help="The path to dbt's manifest file."
    )
    parser.add_argument(
        "--project_id", help="The BigQuery Project ID to leverage."
    )
    parser.add_argument(
        "--keyfile_path", help="The path to the keyfile to use during BQ calls."
    )
    parser.add_argument(
        "--ignored_schemas", help="Folders in models/ to always ignore during row/col checks."
    )
    parser.add_argument(
        "--irregular_schemas", help="Folders in models/ which use 'fallback_prefix' in prod."
    )
    parser.add_argument(
        "--dev_prefix", help="Prefix used by development datasets in dbt."
    )
    parser.add_argument(
        "--prod_prefix", help="Prefix used by production datasets in dbt."
    )
    parser.add_argument(
        "--fallback_prefix", help="Uncommon prefix used by only some production datasets in dbt."
    )
    parser.add_argument(
        "--output_file", help="Where to write results of SQL checks."
    )
    input_args = parser.parse_args()
    return format_args(input_args=input_args)