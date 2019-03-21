from django.db import (
    models as _models,
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

    objects = DeleteRecordQuerySet.as_manager()
