from django.db import (
    models as _models,
)

from .queryset import (
    exclude_exact as _exclude_exact,
)
from ..util.info import (
    ModelInfo as _ModelInfo,
)
from ..util.queryset import (
    initial_queryset as _initial_queryset,
)


class AbstractDeleteRecord(_models.Model):
    _save_check_fields = ('pk',)  # overwrite if the fields to determine 'exist' is not the primary key

    is_deleted = _models.BooleanField(default=False)

    class Meta:
        abstract = True

    @classmethod
    def _model(cls) -> _models.Model:
        return cls

    @classmethod
    def _model_info(cls) -> _ModelInfo:
        return _ModelInfo(cls)

    def _pre_save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        if self._save_check_fields == ('pk',):
            return
        if self.pk is not None:
            return

        try:
            obj = self._model()._base_manager.get(
                **self._model_info().to_dict(self, fields=self._save_check_fields),
            )
        except self.DoesNotExist:
            return

        obj._raw_delete(using=using)

    def save(self, *args, **kwargs):
        self._pre_save(*args, **kwargs)
        return super().save(*args, **kwargs)

    def _raw_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

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
