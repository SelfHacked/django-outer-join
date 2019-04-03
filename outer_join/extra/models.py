from django.db import (
    models as _models,
)

from .queryset import (
    exclude_exact as _exclude_exact,
)
from ..util.queryset import (
    initial_queryset as _initial_queryset,
)


class AbstractDeleteRecord(_models.Model):
    is_deleted = _models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save(using=using)

    class DeleteRecordQuerySet(_models.QuerySet):
        def delete(self):
            self.update(is_deleted=True)

    @_initial_queryset(_exclude_exact('is_deleted', True))
    class DeleteRecordManager(_models.Manager.from_queryset(DeleteRecordQuerySet)):
        pass

    objects = DeleteRecordManager()
