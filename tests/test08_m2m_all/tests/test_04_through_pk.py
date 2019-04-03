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
