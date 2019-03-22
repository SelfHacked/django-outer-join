import pytest

from ..models import A, B, A0, A1


# https://docs.djangoproject.com/en/2.1/ref/models/relations/
# special method to set for related managers:
# create, add, remove, clear, set (2 cases: change and addition only)


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


@pytest.mark.django_db
def test_set_change():
    # set should only work when extending
    with pytest.raises(AttributeError):
        B.objects.get(key=3).a_set.set([A.objects.get(key=2)])


@pytest.mark.django_db
def test_set_add():
    B.objects.get(key=3).a_set.set(A.objects.filter(key__in={2, 3}))
    assert set(A.objects.filter(b__key=3).values_list('key', flat=True)) == {2, 3}
    assert set(B.objects.get(key=3).a_set.values_list('key', flat=True)) == {2, 3}
    assert A0.objects.get(key=2).b.key == 2
    assert A1.objects.get(key=2).b.key == 3
    assert not A0.objects.filter(key=3).exists()
    assert A1.objects.get(key=3).b == 3


# FIXME issue #3
del test_filter_related
del test_add
del test_set_change
del test_set_add
