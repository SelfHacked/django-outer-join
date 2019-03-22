import pytest

from ..models import A, A0, A1


@pytest.mark.django_db
def test_create():
    a = A.objects.create(
        key=5,
        field1=3,
        field3=8,
    )
    # a is not intended to be used directly

    assert not A0.objects.filter(key=5).exists()
    assert A1.objects.filter(key=5).exists()

    a_new = A.objects.get(key=5)
    assert a_new.key == 5
    assert a_new.field1 == 3
    assert a_new.field2 is None
    assert a_new.field3 == 8
    assert a_new.is_deleted is False


@pytest.mark.django_db
def test_save_create():
    a = A(
        key=5,
        field1=3,
        field3=8,
    )
    a.save()  # should create new record in A1

    assert not A0.objects.filter(key=5).exists()
    assert A1.objects.filter(key=5).exists()

    a_new = A.objects.get(key=5)
    assert a_new.key == 5
    assert a_new.field1 == 3
    assert a_new.field2 is None
    assert a_new.field3 == 8
    assert a_new.is_deleted is False


@pytest.mark.django_db
def test_save_a1():
    a = A.objects.get(key=1)  # exists in both A0 and A1
    a.field1 = 7
    a.field3 = 9
    a.save()  # should update A1

    assert A0.objects.get(key=1).field1 == 5  # not updated
    assert A1.objects.get(key=1).field1 == 7  # updated

    a_updated = A.objects.get(key=1)
    assert a_updated.key == 1
    assert a_updated.field1 == 7
    assert a_updated.field2 == 10
    assert a_updated.field3 == 9
    assert a_updated.is_deleted is False


@pytest.mark.django_db
def test_save_a0():
    a = A.objects.get(key=2)  # exists only in A0
    a.field1 = 7
    a.field3 = 9
    a.save()  # should create new record in A1

    assert A0.objects.get(key=2).field1 == 5  # not updated
    assert A1.objects.get(key=2).field1 == 7  # created with new value

    a_updated = A.objects.get(key=2)
    assert a_updated.key == 2
    assert a_updated.field1 == 7
    assert a_updated.field2 == 10
    assert a_updated.field3 == 9
    assert a_updated.is_deleted is False


@pytest.mark.django_db
def test_delete_a1():
    a = A.objects.get(key=1)  # exists in A1
    a.delete()  # should update A1

    assert A0.objects.filter(key=1).exists()  # not deleted
    assert A1.objects.get(key=1).is_deleted is True  # updated is_deleted field

    assert not A.objects.filter(key=1).exists()  # appears deleted


@pytest.mark.django_db
def test_delete_a0():
    a = A.objects.get(key=2)  # exists only in A0
    a.delete()  # should create new record with is_deleted=True

    assert A0.objects.filter(key=2).exists()  # not deleted
    assert A1.objects.get(key=2).is_deleted is True  # create record with is_deleted=True

    assert not A.objects.filter(key=2).exists()  # appears deleted
