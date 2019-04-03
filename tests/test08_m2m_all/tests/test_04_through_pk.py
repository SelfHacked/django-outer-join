import pytest
from django.core.exceptions import FieldError

from ..models import Through


@pytest.mark.django_db
def test_select():
    t = Through.objects.get(pk='1-4')
    assert t.primary_key == '1-4'
    assert t.pk == '1-4'
    assert t.a_id == 1
    assert t.b_id == 4


@pytest.mark.django_db
def test_select_unsupported():
    with pytest.raises(FieldError, match='Unsupported lookup'):
        t = Through.objects.get(pk__in=['1-4'])


@pytest.mark.django_db
def test_save():
    assert not Through.objects.filter(a_id=2, b_id=3).exists()

    t = Through(
        a_id=2,
        b_id=3,
    )
    t.save()

    t = Through.objects.get(a_id=2, b_id=3)
    assert t.primary_key == '2-3'
    assert t.a_id == 2
    assert t.b_id == 3
