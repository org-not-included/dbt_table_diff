# Setup virtual environment (exit by typing "deactivate")
if [ -z "$GH_TOKEN" ]; then
  echo "Running outside PR.."
else
  echo "Running inside PR.."
  work_dir=$1
  cd $work_dir
fi
pip3 install virtualenv
python3 -m virtualenv ./.venv
source ./.venv/bin/activate > /dev/null

# Install dbt and other dependencies
pip3 install -r local-requirements.txt

# Install dbt community packages
dbt deps
# Compile dbt models
dbt compile
# Show profile path
dbt debug --config-dir
