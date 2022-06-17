set -e # fail on error
python //src/applied_cybersec/manage.py check # check for errors in code
curl localhost:8000 # check for startup errors
