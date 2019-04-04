from django.db import models

from outer_join import WritableOuterJoin, OuterJoinInterceptor
from outer_join.extra.models import AbstractDeleteRecord
from outer_join.extra.queryset import exclude_exact


class B(models.Model):
    # This model doesn't need a manual primary key,
    # but it's easier to provide test fixtures
    key = models.IntegerField(primary_key=True)

    val = models.IntegerField()

    class Meta:
        base_manager_name = 'objects'

    interceptor = OuterJoinInterceptor()
    objects = interceptor.get_manager()()


class A0(models.Model):
    key = models.IntegerField(unique=True)
    b = models.ForeignKey(
        B, related_name='+', on_delete=models.CASCADE,
    )

    val = models.IntegerField()


class A1(AbstractDeleteRecord):
    _save_check_fields = ('key',)

    key = models.IntegerField(unique=True)
    b = models.ForeignKey(
        B, related_name='+', on_delete=models.CASCADE,
        null=True,
    )

    val = models.IntegerField(null=True)


class A(models.Model):
    # Manual key must be used for outer-join models with a relation
    # (except through models in m2m relations that are not used directly)
    # However, base tables don't have this restriction
    key = models.IntegerField(primary_key=True)
    b = models.ForeignKey(
        B, related_name='a_set', on_delete=models.CASCADE,
    )

    val = models.IntegerField()

    is_deleted = models.BooleanField(null=True)

    class Meta:
        managed = False
        # IMPORTANT: base manager must be specified for any outer-join model with a relation
        # base manager should not have an initial filter
        base_manager_name = 'base_objects'

    outer_join = WritableOuterJoin(
        A1, A0,
        on='key',
    )
    objects = outer_join.get_manager(
        filter_initial_queryset=exclude_exact('is_deleted', True),
    )()
    base_objects = outer_join.get_manager()()
