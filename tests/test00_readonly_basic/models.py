from django.db import models

from outer_join import OuterJoin


class A0(models.Model):
    key = models.IntegerField(unique=True)

    field1 = models.IntegerField()
    field2 = models.IntegerField()


class A1(models.Model):
    key = models.IntegerField(unique=True)

    field1 = models.IntegerField(null=True)
    field3 = models.IntegerField()


class A(models.Model):
    key = models.IntegerField(unique=True)

    # IMPORTANT: null=True should be set when OUTER JOIN result is nullable
    field1 = models.IntegerField(null=True)
    field2 = models.IntegerField(null=True)
    field3 = models.IntegerField(null=True)

    class Meta:
        managed = False

    outer_join = OuterJoin(
        # Order is IMPORTANT here: A1.field1 will take precedence before A0.field1
        A1, A0,
        on='key',
    )
    objects = outer_join.get_manager()()
