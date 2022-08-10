# Setup virtual environment (exit by typing "deactivate")
work_dir=$1
cd $work_dir
pip3 install virtualenv
python3 -m virtualenv ./.venv
source ./.venv/bin/activate > /dev/null

# Install dbt and other dependencies
pip install -r local-requirements.txt

# Install dbt community packages
dbt deps
# Compile dbt models
dbt compile
# Show profile path
dbt debug --config-dir
