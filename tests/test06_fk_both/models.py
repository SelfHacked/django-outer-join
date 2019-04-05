from django.db import models

from outer_join import WritableOuterJoin
from outer_join.extra.models import AbstractDeleteRecord
from outer_join.extra.queryset import exclude_exact


class B0(models.Model):
    key = models.IntegerField(unique=True)

    val = models.IntegerField()


class B1(AbstractDeleteRecord):
    _save_check_fields = ('key',)

    key = models.IntegerField(unique=True)

    val = models.IntegerField(null=True)


class B(models.Model):
    key = models.IntegerField(primary_key=True)

    val = models.IntegerField(null=True)

    is_deleted = models.BooleanField(null=True)

    class Meta:
        managed = False
        base_manager_name = 'base_objects'

    outer_join = WritableOuterJoin(
        B1, B0,
        on='key',
    )
    objects = outer_join.get_manager(
        filter_initial_queryset=exclude_exact('is_deleted', True),
    )()
    base_objects = outer_join.get_manager()()


class A0(models.Model):
    key = models.IntegerField(unique=True)
    b = models.ForeignKey(
        # readonly models can have foreign keys to real tables with db_constraint
        B0, related_name='+', on_delete=models.CASCADE,
    )

    val = models.IntegerField()


class A1(AbstractDeleteRecord):
    _save_check_fields = ('key',)

    key = models.IntegerField(unique=True)
    b = models.ForeignKey(
        # read-write models should reference the outer-join model
        B, related_name='+', on_delete=models.CASCADE,
        # and should not have db_constraint
        db_constraint=False,
        null=True,
    )

    val = models.IntegerField(null=True)


class A(models.Model):
    key = models.IntegerField(primary_key=True)
    b = models.ForeignKey(
        B, related_name='a_set', on_delete=models.CASCADE,
        db_constraint=False,
    )

    val = models.IntegerField()

    is_deleted = models.BooleanField(null=True)

    class Meta:
        managed = False
        base_manager_name = 'base_objects'

    outer_join = WritableOuterJoin(
        A1, A0,
        on='key',
    )
    objects = outer_join.get_manager(
        filter_initial_queryset=exclude_exact('is_deleted', True),
    )()
    base_objects = outer_join.get_manager()()
