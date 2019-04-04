#!/bin/bash

django_version="$(python -c "import django; print(django.__version__[:3])")"

if [[ "${django_version}" == "2.0" ]]
then
    # django 2.0 requires NullBooleanField instead of BooleanField(null=True)
    echo "Using django 2.0, skipping"
    exit 0
fi

result=".makemigrations"
python manage.py makemigrations > ${result}

code=$?
if [[ ${code} != 0 ]]
then
    echo "makemigrations exited with ${code}"
    exit ${code}
fi

expect="No changes detected"
if [[ "$(cat ${result})" == "${expect}" ]]
then
    exit 0
else
    echo "makemigrations is not clean (expect '${expect}'):"
    cat ${result}
    exit 2
fi
