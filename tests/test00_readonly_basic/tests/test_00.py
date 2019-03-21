import pytest

from ..models import A


@pytest.mark.django_db
def test_count():
    assert A.objects.count() == 3


@pytest.mark.django_db
def test_get_a0():
    a = A.objects.get(key=2)  # exists in A0 table only
    assert a.key == 2
    assert a.field1 == 5
    assert a.field2 == 10
    assert a.field3 is None


@pytest.mark.django_db
def test_get_a1():
    a = A.objects.get(key=3)  # exists in A1 table only
    assert a.key == 3
    assert a.field1 == 6
    assert a.field2 is None
    assert a.field3 == 30


@pytest.mark.django_db
def test_get_both():
    a = A.objects.get(key=1)  # exists in both tables
    assert a.key == 1
    assert a.field1 == 6  # overwritten by A1
    assert a.field2 == 10
    assert a.field3 == 20


@pytest.mark.django_db
def test_filter():
    assert set(A.objects.filter(field1=5).values_list('key', flat=True)) == {2}
    assert set(A.objects.filter(field1=6).values_list('key', flat=True)) == {1, 3}
