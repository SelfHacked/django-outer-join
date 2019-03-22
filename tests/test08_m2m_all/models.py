from django.db import models

from outer_join import WritableOuterJoin
from outer_join.extra.models import AbstractDeleteRecord
from outer_join.extra.queryset import exclude_exact


class B0(models.Model):
    key = models.IntegerField(unique=True)

    val = models.IntegerField()


class B1(AbstractDeleteRecord):
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
    # this M2M field is optional because it's not an actual table column
    # however since A0, B0 and Through0 are all readonly,
    # we may put this field here for easier access
    b_set = models.ManyToManyField(
        B0, related_name='a_set', through='Through0',
    )

    val = models.IntegerField()


class A1(AbstractDeleteRecord):
    key = models.IntegerField(unique=True)

    val = models.IntegerField(null=True)


class A(models.Model):
    key = models.IntegerField(primary_key=True)
    b_set = models.ManyToManyField(
        B, related_name='a_set', through='Through',
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


class Through0(models.Model):
    a = models.ForeignKey(
        A0, related_name='+', on_delete=models.CASCADE,
    )
    b = models.ForeignKey(
        B0, related_name='+', on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = (
            ('a', 'b'),
        )


class Through1(AbstractDeleteRecord):
    a = models.ForeignKey(
        A, related_name='+', on_delete=models.CASCADE,
        db_constraint=False,
    )
    b = models.ForeignKey(
        B, related_name='+', on_delete=models.CASCADE,
        db_constraint=False,
    )

    class Meta:
        unique_together = (
            ('a', 'b'),
        )


class Through(models.Model):
    a = models.ForeignKey(
        A, related_name='+', on_delete=models.CASCADE,
        db_constraint=False,
    )
    b = models.ForeignKey(
        B, related_name='+', on_delete=models.CASCADE,
        db_constraint=False,
    )

    is_deleted = models.BooleanField(null=True)

    class Meta:
        unique_together = (
            ('a', 'b'),
        )
        managed = False
        base_manager_name = 'base_objects'

    outer_join = WritableOuterJoin(
        Through1, Through0,
        on=['a', 'b'],
    )
    objects = outer_join.get_manager(
        filter_initial_queryset=exclude_exact('is_deleted', True),
    )()
    base_objects = outer_join.get_manager()()
