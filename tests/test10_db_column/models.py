from django.db import models

from outer_join import WritableOuterJoin, OuterJoin
from outer_join.extra.models import AbstractDeleteRecord
from outer_join.extra.queryset import exclude_exact, filter_exact


class A0(models.Model):
    key = models.IntegerField(
        unique=True,
        db_column='xxx',
    )

    field1 = models.IntegerField(
        db_column='yyy',
    )
    field2 = models.IntegerField(
        db_column='zzz',
    )


class A1(AbstractDeleteRecord):
    key = models.IntegerField(
        unique=True,
        db_column='aaa',
    )

    # IMPORTANT null=True should be set for all non-ON fields in a DeleteRecord
    field1 = models.IntegerField(
        null=True,
        db_column='bbb',
    )
    field3 = models.IntegerField(
        null=True,
        db_column='ccc',
    )

    _save_check_fields = ('key',)


class A(models.Model):
    key = models.IntegerField(unique=True)

    field1 = models.IntegerField(null=True)
    field2 = models.IntegerField(null=True)
    field3 = models.IntegerField(null=True)

    is_deleted = models.BooleanField(null=True)

    class Meta:
        managed = False

    outer_join = WritableOuterJoin(
        A1, A0,
        on='key',
    )
    objects = outer_join.get_manager(
        filter_initial_queryset=exclude_exact('is_deleted', True),
    )()

    readonly_outer_join = OuterJoin(
        A1, A0,
        on='key',
    )
    all_objects = readonly_outer_join.get_manager()()
    deleted_objects = readonly_outer_join.get_manager(
        filter_initial_queryset=filter_exact('is_deleted', True),
    )()
