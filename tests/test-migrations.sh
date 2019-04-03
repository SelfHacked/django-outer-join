#!/bin/bash

django_version="$(python -c "import django; print(django.__version__[:3])")"

if [[ "${django_version}" == "2.0" ]]
then
    # django 2.0 requires NullBooleanField instead of BooleanField(null=True)
    exit 0
fi

result=".makemigrations"
python manage.py makemigrations > ${result}

code=$?
if [[ ${code} != 0 ]]
then
    exit ${code}
fi

if [[ "$(cat ${result})" == "No changes detected" ]]
then
    exit 0
else
    exit 2
fi
