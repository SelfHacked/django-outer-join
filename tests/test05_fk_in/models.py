from django.db import models

from outer_join import WritableOuterJoin
from outer_join.extra.models import AbstractDeleteRecord
from outer_join.extra.queryset import exclude_exact


class B0(models.Model):
    key = models.IntegerField(primary_key=True)

    val = models.IntegerField()


class B1(AbstractDeleteRecord):
    key = models.IntegerField(primary_key=True)

    val = models.IntegerField(null=True)


class B(models.Model):
    # IMPORTANT: must have manual primary key
    key = models.IntegerField(primary_key=True)

    val = models.IntegerField(null=True)

    is_deleted = models.BooleanField(null=True)

    class Meta:
        managed = False

    outer_join = WritableOuterJoin(
        B1, B0,
        on='key',
    )
    objects = outer_join.get_manager(
        filter_initial_queryset=exclude_exact('is_deleted', True),
    )()


class A(models.Model):
    key = models.IntegerField(unique=True)
    b = models.ForeignKey(
        B, related_name='a_set', on_delete=models.SET_NULL,
        db_constraint=False,
        null=True,
    )
