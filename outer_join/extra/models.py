import django.db.models as _models

from outer_join.util.info import (
    ModelInfo as _ModelInfo,
)
from outer_join.util.queryset import (
    initial_queryset as _initial_queryset,
    QuerySetSplit as _QuerySetSplit,
)
from .queryset import (
    exclude_exact as _exclude_exact,
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
        pk_field_name = self._model_info().pk.name
        pk_check = (
                'pk' in self._save_check_fields or
                pk_field_name in self._save_check_fields
        )
        if pk_check and len(self._save_check_fields) != 1:
            raise ValueError('Cannot have pk and another field in _save_check_fields at the same time')

        try:
            obj = self._model()._base_manager.get(
                **self._model_info().to_dict(self, fields=self._save_check_fields),
            )
        except self.DoesNotExist:
            obj = None
        else:
            if obj.is_deleted:
                obj._base_delete(using=using)
                obj = None

        if not pk_check:
            if obj is None:
                self.pk = None
            else:
                self.pk = obj.pk

    def save(self, *args, **kwargs):
        self._pre_save(*args, **kwargs)
        return super().save(*args, **kwargs)

    def _base_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save(using=using)

    class DeleteRecordQuerySet(_models.QuerySet):
        def bulk_create(self, objs, batch_size=None):
            split = _QuerySetSplit(
                objs,
                self.model,
                *self.model._save_check_fields,
                manager='_base_manager',
            )
            split.get_existing_queryset().delete()
            return super().bulk_create(objs, batch_size=batch_size)

        def _base_delete(self):
            return super().delete()

        def delete(self):
            self.update(is_deleted=True)

    @_initial_queryset(_exclude_exact('is_deleted', True))
    class DeleteRecordManager(_models.Manager.from_queryset(DeleteRecordQuerySet)):
        pass

    objects = DeleteRecordManager()
