from django.db import models

from outer_join import WritableOuterJoin
from outer_join.extra.models import AbstractDeleteRecord
from outer_join.extra.queryset import exclude_exact


class B(models.Model):
    # This model doesn't need a manual primary key,
    # but it's easier to provide test fixtures
    key = models.IntegerField(primary_key=True)

    val = models.IntegerField()


class A0(models.Model):
    key = models.IntegerField(unique=True)
    b = models.ForeignKey(
        B, related_name='+', on_delete=models.CASCADE,
    )


class A1(AbstractDeleteRecord):
    key = models.IntegerField(unique=True)
    b = models.ForeignKey(
        B, related_name='+', on_delete=models.CASCADE,
        null=True,
    )


class A(models.Model):
    key = models.IntegerField(unique=True)
    b = models.ForeignKey(
        B, related_name='a_set', on_delete=models.CASCADE,
    )

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
