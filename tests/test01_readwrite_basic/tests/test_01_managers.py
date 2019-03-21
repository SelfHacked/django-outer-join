import pytest

from ..models import A


@pytest.mark.django_db
def test_all():
    assert A.all_objects.count() == 4


@pytest.mark.django_db
def test_deleted():
    assert A.deleted_objects.count() == 1
    assert A.deleted_objects.get().key == 4
