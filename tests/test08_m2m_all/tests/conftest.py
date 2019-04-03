import os

import pytest
from django.core.management import call_command


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    app = os.path.dirname(os.path.dirname(__file__))
    with django_db_blocker.unblock():
        call_command('loaddata', os.path.join(app, 'tests', 'fixture.json'))
