from setuptools import setup, find_packages
from pathlib import Path


VERSION = '2.2.0'
DESCRIPTION = 'Compares models in dbt during an open PR'
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="dbt_table_diff",
    version=VERSION,
    url="https://github.com/org-not-included/dbt_table_diff/",
    author="mtsadler (Mike Sadler)",
    author_email="<michaeltsadler1@gmail.com>",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'dbt-bigquery==1.0.0',
        'google-cloud-bigquery==2.34.4',
        'jinja2==2.11.3',
        'markupsafe==2.0.1',
        'pandas==1.4.3',
        'pandas-gbq==0.17.8',
        'py-github-helper>=0.2.2'
    ],
    keywords=['bigquery', 'qa', 'sql', 'table', 'comment', 'check', 'Pull Request', 'dbt', 'cicd'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)