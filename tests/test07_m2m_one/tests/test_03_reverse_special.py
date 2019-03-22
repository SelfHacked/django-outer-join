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
    B.objects.get(key=1).a_set.add(A.objects.get(key=1))
    # add relation 1-1
    assert set(A.objects.get(key=1).b_set.values_list('key', flat=True)) == {1, 4}
    assert set(B.objects.get(key=1).a_set.values_list('key', flat=True)) == {1}


@pytest.mark.django_db
def test_create():
    B.objects.get(key=1).a_set.create(
        key=5,
        val=0,
    )
    # create relation 1-5
    assert set(A.objects.get(key=5).b_set.values_list('key', flat=True)) == {1}
    assert set(B.objects.get(key=1).a_set.values_list('key', flat=True)) == {5}


@pytest.mark.django_db
def test_remove():
    B.objects.get(key=3).a_set.remove(A.objects.get(key=3))
    # remove relation 3-3
    assert A.objects.get(key=3).b_set.count() == 0
    assert B.objects.get(key=3).a_set.count() == 0


@pytest.mark.django_db
def test_clear():
    B.objects.get(key=4).a_set.clear()
    # remove relation 4-1
    assert A.objects.get(key=1).b_set.count() == 0
    assert B.objects.get(key=4).a_set.count() == 0


@pytest.mark.django_db
def test_set_change():
    B.objects.get(key=3).a_set.set([A.objects.get(key=2)])
    # add relation 3-2, remove relation 3-3
    assert set(A.objects.get(key=2).b_set.values_list('key', flat=True)) == {2, 3}
    assert A.objects.get(key=3).b_set.count() == 0
    assert set(B.objects.get(key=3).a_set.values_list('key', flat=True)) == {2}


@pytest.mark.django_db
def test_set_add():
    B.objects.get(key=3).a_set.set(A.objects.filter(key__in={2, 3}))
    # add relation 3-2
    assert set(A.objects.get(key=2).b_set.values_list('key', flat=True)) == {2, 3}
    assert set(B.objects.get(key=3).a_set.values_list('key', flat=True)) == {2, 3}
