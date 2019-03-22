"""
Copied from test07
"""

import pytest

from ..models import A, B


# https://docs.djangoproject.com/en/2.1/ref/models/relations/
# special method to set for related managers:
# create, add, remove, clear, set (2 cases: change and addition only)
# when using a through model, create, add, remove and set are disabled


@pytest.mark.django_db
def test_add():
    with pytest.raises(AttributeError):
        B.objects.get(key=1).a_set.add(A.objects.get(key=1))


@pytest.mark.django_db
def test_create():
    with pytest.raises(AttributeError):
        B.objects.get(key=1).a_set.create(
            key=5,
            val=0,
        )


@pytest.mark.django_db
def test_remove():
    with pytest.raises(AttributeError):
        B.objects.get(key=3).a_set.remove(A.objects.get(key=3))


@pytest.mark.django_db
def test_clear():
    B.objects.get(key=4).a_set.clear()
    # remove relation 4-1
    assert A.objects.get(key=1).b_set.count() == 0
    assert B.objects.get(key=4).a_set.count() == 0


@pytest.mark.django_db
def test_set_change():
    with pytest.raises(AttributeError):
        B.objects.get(key=3).a_set.set([A.objects.get(key=2)])


@pytest.mark.django_db
def test_set_add():
    with pytest.raises(AttributeError):
        B.objects.get(key=3).a_set.set(A.objects.filter(key__in={2, 3}))
