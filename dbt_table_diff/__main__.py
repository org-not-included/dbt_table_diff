import logging
from run_sql_checks import parse_flags_and_run


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.ERROR)
    print(parse_flags_and_run())
    exit(0)
