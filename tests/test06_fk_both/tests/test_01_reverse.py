"""
Copied from test04
"""

import pytest

from ..models import A, B, A0, A1


@pytest.mark.django_db
def test_select():
    assert B.objects.get(key=1).a_set.count() == 0
    assert set(B.objects.get(key=2).a_set.values_list('key', flat=True)) == {2}
    assert set(B.objects.get(key=3).a_set.values_list('key', flat=True)) == {3}
    assert set(B.objects.get(key=4).a_set.values_list('key', flat=True)) == {1}


@pytest.mark.django_db
def test_filter_related():
    assert B.objects.get(a_set__key=1).key == 4
    assert B.objects.get(a_set__val=200).key == 2


@pytest.mark.django_db
def test_prefetch_related(django_assert_num_queries):
    b = B.objects.prefetch_related('a_set').get(key=2)

    with django_assert_num_queries(0):
        assert {a.key for a in b.a_set.all()} == {2}


@pytest.mark.django_db
def test_qs_update():
    B.objects.get(key=4).a_set.update(val=1000)
    assert A.objects.get(key=1).val == 1000
    assert A0.objects.get(key=1).val == 100
    assert A1.objects.get(key=1).val == 1000


@pytest.mark.django_db
def test_qs_delete():
    B.objects.get(key=2).a_set.all().delete()
    assert not A.objects.filter(key=2).exists()
    assert A0.objects.filter(key=2).exists()
    assert A1.objects.get(key=2).is_deleted is True
