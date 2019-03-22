import pytest

from ..models import A


@pytest.mark.django_db
def test_fk():
    assert A.objects.get(key=1).b.key == 4
    assert A.objects.get(key=2).b.key == 2
    assert A.objects.get(key=3).b.key == 3


@pytest.mark.django_db
def test_filter_fk():
    assert set(A.objects.filter(b__val=20).values_list('key', flat=True)) == {1}


@pytest.mark.django_db
def test_select_related(django_assert_num_queries):
    with django_assert_num_queries(1):
        assert A.objects.select_related('b').get(key=1).b.val == 20
    with django_assert_num_queries(1):
        assert A.objects.select_related('b').get(key=2).b.val == 10
    with django_assert_num_queries(1):
        assert A.objects.select_related('b').get(key=3).b.val == 15
