"""
Copied from test04
"""

import pytest

from ..models import A, B, B0, B1


@pytest.mark.django_db
def test_select():
    assert set(A.objects.get(key=1).b_set.values_list('key', flat=True)) == {4}
    assert set(A.objects.get(key=2).b_set.values_list('key', flat=True)) == {2}
    assert set(A.objects.get(key=3).b_set.values_list('key', flat=True)) == {3}


@pytest.mark.django_db
def test_filter_related():
    assert A.objects.get(b_set__key=4).key == 1
    assert set(A.objects.filter(b_set__val=10).values_list('key', flat=True)) == {1, 2}


@pytest.mark.django_db
def test_prefetch_related(django_assert_num_queries):
    b = A.objects.prefetch_related('b_set').get(key=2)

    with django_assert_num_queries(0):
        assert {a.key for a in b.b_set.all()} == {2}


@pytest.mark.django_db
def test_qs_update():
    A.objects.get(key=1).b_set.update(val=1000)
    assert B.objects.get(key=4).val == 1000
    assert B0.objects.get(key=4).val == 10
    assert B1._base_manager.get(key=4).val == 1000


@pytest.mark.django_db
def test_qs_delete():
    A.objects.get(key=2).b_set.all().delete()
    assert not B.objects.filter(key=2).exists()
    assert B0.objects.filter(key=2).exists()
    assert B1._base_manager.get(key=2).is_deleted is True
