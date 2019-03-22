from django.db import models

from outer_join import OuterJoin


class A0(models.Model):
    key1 = models.IntegerField()
    key2 = models.IntegerField()

    field1 = models.IntegerField()
    field2 = models.IntegerField()

    class Meta:
        unique_together = (
            ('key1', 'key2'),
        )


class A1(models.Model):
    key1 = models.IntegerField()
    key2 = models.IntegerField()

    field1 = models.IntegerField(null=True)
    field3 = models.IntegerField()

    class Meta:
        unique_together = (
            ('key1', 'key2'),
        )


class A(models.Model):
    key1 = models.IntegerField()
    key2 = models.IntegerField()

    field1 = models.IntegerField(null=True)
    field2 = models.IntegerField(null=True)
    field3 = models.IntegerField(null=True)

    class Meta:
        unique_together = (
            ('key1', 'key2'),
        )
        managed = False

    outer_join = OuterJoin(
        A1, A0,
        on=['key1', 'key2'],
    )
    objects = outer_join.get_manager()()
