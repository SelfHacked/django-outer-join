import pytest

from ..models import Through


@pytest.mark.django_db
def test_select():
    t = Through.objects.get(pk='1-4')
    assert t.a_id == 1
    assert t.b_id == 4
