import argparse


def fetch_input_args():
    """
    Parse user input args from the command line into variables.
    """
    parser = argparse.ArgumentParser("simple_example")
    parser.add_argument(
        "-o", "--org_name", help="Owner of GitHub repository."
    )
    parser.add_argument(
        "-r", "--repo_name", help="Name of the GitHub repository."
    )
    parser.add_argument(
        "-t", "--auth_token", help="User's GitHub Personal Access Token."
    )
    parser.add_argument(
        "-l", "--pr_id", help="The issue # of the Pull Request.",
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
    parser.add_argument(
        "--custom_checks_path", help="A local folder containing any custom SQL to run."
    )
    return parser.parse_args()
