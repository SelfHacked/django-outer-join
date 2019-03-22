"""
Copied from test04
"""

import pytest

from ..models import A, B


# https://docs.djangoproject.com/en/2.1/ref/models/relations/
# special method to set for related managers:
# create, add, remove, clear, set (2 cases: change and addition only)


@pytest.mark.django_db
def test_add():
    A.objects.get(key=1).b_set.add(B.objects.get(key=1))
    # add relation 1-1
    assert set(B.objects.get(key=1).a_set.values_list('key', flat=True)) == {1}
    assert set(A.objects.get(key=1).b_set.values_list('key', flat=True)) == {1, 4}


@pytest.mark.django_db
def test_create():
    A.objects.get(key=1).b_set.create(
        key=5,
        val=0,
    )
    # add relation 1-5
    assert set(B.objects.get(key=5).a_set.values_list('key', flat=True)) == {1}
    assert set(A.objects.get(key=1).b_set.values_list('key', flat=True)) == {4, 5}


@pytest.mark.django_db
def test_remove():
    A.objects.get(key=3).b_set.remove(B.objects.get(key=3))
    # remove relation 3-3
    assert B.objects.get(key=3).a_set.count() == 0
    assert A.objects.get(key=3).b_set.count() == 0


@pytest.mark.django_db
def test_clear():
    A.objects.get(key=1).b_set.clear()
    # remove relation 1-4
    assert B.objects.get(key=4).a_set.count() == 0
    assert A.objects.get(key=1).b_set.count() == 0


@pytest.mark.django_db
def test_set_change():
    A.objects.get(key=3).b_set.set([B.objects.get(key=2)])
    # add relation 3-2, remove relation 3-3
    assert set(B.objects.get(key=2).a_set.values_list('key', flat=True)) == {2, 3}
    assert B.objects.get(key=3).a_set.count() == 0
    assert set(A.objects.get(key=3).b_set.values_list('key', flat=True)) == {2}


@pytest.mark.django_db
def test_set_add():
    A.objects.get(key=3).b_set.set(B.objects.filter(key__in={2, 3}))
    # add relation 3-2
    assert set(B.objects.get(key=2).a_set.values_list('key', flat=True)) == {2, 3}
    assert set(A.objects.get(key=3).b_set.values_list('key', flat=True)) == {2, 3}
