"""
Copied from test07
"""

import pytest

from tests.outer_join_test.util import skip_2_2_related_manager
from ..models import A, B


# https://docs.djangoproject.com/en/2.1/ref/models/relations/
# special method to set for related managers:
# create, add, remove, clear, set (2 cases: change and addition only)
# when using a through model, create, add, remove and set are disabled


@skip_2_2_related_manager
@pytest.mark.django_db
def test_add():
    with pytest.raises(AttributeError):
        A.objects.get(key=1).b_set.add(B.objects.get(key=1))


@skip_2_2_related_manager
@pytest.mark.django_db
def test_create():
    with pytest.raises(AttributeError):
        A.objects.get(key=1).b_set.create(
            key=5,
            val=0,
        )


@skip_2_2_related_manager
@pytest.mark.django_db
def test_remove():
    with pytest.raises(AttributeError):
        A.objects.get(key=3).b_set.remove(B.objects.get(key=3))


@pytest.mark.django_db
def test_clear():
    A.objects.get(key=1).b_set.clear()
    # remove relation 1-4
    assert B.objects.get(key=4).a_set.count() == 0
    assert A.objects.get(key=1).b_set.count() == 0


@skip_2_2_related_manager
@pytest.mark.django_db
def test_set_change():
    with pytest.raises(AttributeError):
        A.objects.get(key=3).b_set.set([B.objects.get(key=2)])


@skip_2_2_related_manager
@pytest.mark.django_db
def test_set_add():
    with pytest.raises(AttributeError):
        A.objects.get(key=3).b_set.set(B.objects.filter(key__in={2, 3}))
