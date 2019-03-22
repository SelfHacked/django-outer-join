"""
Copied from test04
"""

import pytest

from ..models import A, B, A0, A1


# https://docs.djangoproject.com/en/2.1/ref/models/relations/
# special method to set for related managers:
# create, add, remove, clear, set (2 cases: change and addition only)
# without null=True in ForeignKey, remove and clear with raise AttributeError,
# and set will fallback to add


@pytest.mark.django_db
def test_add():
    B.objects.get(key=1).a_set.add(A.objects.get(key=1))
    assert A.objects.get(key=1).b.key == 1
    assert set(B.objects.get(key=1).a_set.values_list('key', flat=True)) == {1}
    assert B.objects.get(key=4).a_set.count() == 0
    assert A0.objects.get(key=1).b.key == 1
    assert A1.objects.get(key=1).b.key == 1


@pytest.mark.django_db
def test_create():
    B.objects.get(key=1).a_set.create(
        key=5,
    )
    assert A.objects.get(key=5).b.key == 1
    assert set(B.objects.get(key=1).a_set.values_list('key', flat=True)) == {5}
    assert not A0.objects.filter(key=5).exists()
    assert A1.objects.get(key=5).b.key == 1


@pytest.mark.django_db
def test_remove():
    # remove should not work without null=True on ForeignKey
    with pytest.raises(AttributeError):
        B.objects.get(key=3).a_set.remove(A.objects.get(key=3))


@pytest.mark.django_db
def test_clear():
    # clear should not work without null=True on ForeignKey
    with pytest.raises(AttributeError):
        B.objects.get(key=4).a_set.clear()
