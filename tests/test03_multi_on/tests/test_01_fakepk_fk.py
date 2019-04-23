from django.db import connection

from ..models import B


def test_db_type():
    assert B._meta.get_field('a').db_type(connection=connection) == 'text'
