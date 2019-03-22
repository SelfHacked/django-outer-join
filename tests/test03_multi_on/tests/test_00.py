"""
Copied from test00
Should work exactly the same
"""

import pytest

from ..models import A


@pytest.mark.django_db
def test_count():
    assert A.objects.count() == 3


@pytest.mark.django_db
def test_get_a0():
    a = A.objects.get(key1=1, key2=2)  # exists in A0 table only
    assert a.key1 == 1
    assert a.key2 == 2
    assert a.field1 == 5
    assert a.field2 == 10
    assert a.field3 is None


@pytest.mark.django_db
def test_get_a1():
    a = A.objects.get(key1=2, key2=1)  # exists in A1 table only
    assert a.key1 == 2
    assert a.key2 == 1
    assert a.field1 == 6
    assert a.field2 is None
    assert a.field3 == 30


@pytest.mark.django_db
def test_get_both():
    a = A.objects.get(key1=1, key2=1)  # exists in both tables
    assert a.key1 == 1
    assert a.key2 == 1
    assert a.field1 == 6  # overwritten by A1
    assert a.field2 == 10
    assert a.field3 == 20


@pytest.mark.django_db
def test_filter():
    assert set(A.objects.filter(field1=5).values_list('key1', 'key2')) == {(1, 2)}
    assert set(A.objects.filter(field1=6).values_list('key1', 'key2')) == {(1, 1), (2, 1)}
    assert set(A.objects.filter(field2=10).values_list('key1', 'key2')) == {(1, 1), (1, 2)}
