#!/bin/bash
/wait
file='/setup/init.log'
if [ -f "$file" ]; then
    echo "system alredy set up, skipping initialization"
else
    python /src/applied_cybersec/manage.py makemigrations
    echo "--------------------------------------------------------"
    python /src/applied_cybersec/manage.py migrate
    echo "--------------------------------------------------------"
    python /src/applied_cybersec/manage.py collectstatic --noinput
    echo "--------------------------------------------------------"
    django-admin compilemessages
    echo "--------------------------------------------------------"
    python /src/applied_cybersec/manage.py createsuperuser --noinput
    # if superuser exists, data is assumed to be already imported
    # if last command succeeds, no superuser exists, so import data
    if [ $? -eq 0 ]; then
        echo "--------------------------------------------------------"
        echo "" >/setup/init.log
        echo "system alredy set up, skipping initialization"
    fi
fi

echo "--------------------------------------------------------"

if python /src/applied_cybersec/manage.py test --no-input --failfast ; then
    echo "Tests succeeded"
else
    echo "Tests failed, exiting ..."
    exit 1
fi

echo "--------------------------------------------------------"

# if environment variable DJANGO_AUTO_RELOAD is set to 1, true or yes, run in debug mode, otherwise run in production mode
if [ "$DJANGO_AUTO_RELOAD" = "1" ] || [ "$DJANGO_AUTO_RELOAD" = "true" ] || [ "$DJANGO_AUTO_RELOAD" = "yes" ]; then
    echo "starting django with auto page reloading"
    exec python //src/applied_cybersec/manage.py runserver 0.0.0.0:8000
else
    echo "starting django without auto page reloading"
    exec python //src/applied_cybersec/manage.py runserver 0.0.0.0:8000 --noreload
fi