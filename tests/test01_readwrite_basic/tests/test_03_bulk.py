import pytest

from ..models import A, A0, A1


@pytest.mark.django_db
def test_bulk_create():
    A.objects.bulk_create([
        A(
            key=5,
            field1=3,
        ),
        A(
            key=6,
            field3=9,
        ),
    ])

    assert not A0.objects.filter(key__in=[5, 6]).exists()
    assert A1.objects.filter(key__in=[5, 6]).count() == 2

    assert A.objects.filter(key__in=[5, 6]).count() == 2


@pytest.mark.django_db
def test_batch_update():
    A.objects.update(field1=15)
    # should update key=(1, 3) with field1
    # should create key=2 with field1
    # should not change key=4 (deleted)

    assert set(A0.objects.values_list('key', flat=True)) == {1, 2, 4}
    assert set(A1.objects.values_list('key', flat=True)) == {1, 2, 3, 4}
    assert set(A.objects.values_list('key', flat=True)) == {1, 2, 3}

    assert A0.objects.get(key=1).field1 == 5
    assert A0.objects.get(key=2).field1 == 5
    assert A0.objects.get(key=4).field1 == 5

    assert A1.objects.get(key=1).field1 == 15
    assert A1.objects.get(key=2).field1 == 15
    assert A1.objects.get(key=3).field1 == 15
    assert A1.objects.get(key=4).field1 is None

    assert A.objects.get(key=1).field1 == 15
    assert A.objects.get(key=2).field1 == 15
    assert A.objects.get(key=3).field1 == 15


@pytest.mark.django_db
def test_batch_delete():
    A.objects.filter(field2=10).delete()
    # should update key=1 with is_deleted=True
    # should create key=2 with is_deleted=True

    assert set(A0.objects.values_list('key', flat=True)) == {1, 2, 4}
    assert set(A1.objects.values_list('key', flat=True)) == {1, 2, 3, 4}
    assert set(A.objects.values_list('key', flat=True)) == {3}

    assert A1.objects.get(key=1).is_deleted is True
    assert A1.objects.get(key=2).is_deleted is True
