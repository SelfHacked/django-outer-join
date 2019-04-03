# django-outer-join

[![Build Status](https://travis-ci.com/SelfHacked/django-outer-join.svg?branch=master)](https://travis-ci.com/SelfHacked/django-outer-join)
[![Coverage Status](https://coveralls.io/repos/github/SelfHacked/django-outer-join/badge.svg?branch=master)](https://coveralls.io/github/SelfHacked/django-outer-join?branch=master)

## Introduction

Django does not have `OUTER JOIN` functionality,
and this library intend to introduce outer joins into the Django ORM.

And `OUTER JOIN` is emulated by creating an unmanaged model:

```python
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

    field1 = models.IntegerField(null=True)
    field2 = models.IntegerField(null=True)
    field3 = models.IntegerField(null=True)

    class Meta:
        managed = False

    outer_join = OuterJoin(
        A1, A0,
        on='key',
    )
    objects = outer_join.get_manager()()
```

By overwriting the manager, we intercept the `SELECT` statement
and turn it into an `OUTER JOIN` with underlying tables.

When there is a field that exists in more than one model (e.g. `field1` above),
a `COALESCE` is used in the order the models are passed into `OuterJoin`.
You can think of it as `A1.field1` overwrites `A0.field1` if `A1.field1` is not null.

## Compatibility

* Python >= 3.6 (because we love type hints)
* Django >= 2
* PostgreSQL
    * We only test/support Postgres
    * Does not work with sqlite because it doesn't have `OUTER JOIN`
    * Django use different `SQLCompiler` classes for MySQL and Oracle, so they most likely will have issues
    * Should work fine with other SQLs

## Examples

See models and tests under the [`tests`](tests/) folder, which is a Django project.
Each app is a use case, which contains a full set of models
and potential usages in test files.

## Installation

```bash
pip install git+git://github.com/SelfHacked/django-outer-join.git#egg=django-outer-join
```

## Usage

### The `OuterJoin` Class

The `outer_join.OuterJoin` class provides **read-only** access.
It should be declared within a model (on the same level as fields and managers).
It is only intended to provide managers and will not be accessible at runtime.

* `__init__`
    * `*models: Type[Model]`
        * At least must be provided.
        * Order is important because the way `COALESCE` works.
    * `queryset: Type[QuerySet]`
        * A base queryset class for all managers.
    * `on: Union[str, Sequence[str]]`
        * Field(s) to join on.
* `get_manager -> Type[Manager]`
    * `*` (force kwargs, see [PEP 3102](https://www.python.org/dev/peps/pep-3102/))
    * `filter_initial_queryset: Union[QuerySetFilter, Sequence[QuerySetFilter], None]`
        * `QuerySetFilter` is a function (`Queryset`) -> `QuerySet`. See [`outer_join.extra.queryset`](outer_join/extra/queryset.py) for convenience implementations.
        * When multiple functions are provided, they will be applied in order.

For the model itself, all fields that can be null from an outer join result should have `null=True`.
The model must have `managed = False` (obviously),
and all managers should be generated from `get_manager` method.

### The `WritableOuterJoin` Class

The `outer_join.WritableOuterJoin` class provides read-write access.
It is inherited from the `OuterJoin` class.

The first model will be used as read-write, and others will be read-only.

To make deletions logically work, we provide a convenience class
`outer_join.extra.models.AbstractDeleteRecord`
which is an abstract model with a boolean field `is_deleted`
and overwrites deletion methods.
The default manager (`objects`) should also have an initial filter.
See [`test01`](tests/test01_readwrite_basic/models.py) for example.

Because of how `COALESCE` works,
setting a field to null will only set it to null in the read-write table,
and it will revert to whatever value read-only table(s) provide.

The read-write model should have `null=True` or `default=`
for all fields that are not `on`.

Be careful with objects returned from `create` or calling the class constructor,
since they will not contain any information from the database,
even after they have been saved.

### Relations

Whenever there is a relation that involves a outer-join model, including

* ForeignKey from
* ForeignKey to
* M2M

extra steps must be taken for the outer-join model itself.

1. The outer-join model must have a manual primary key, with the exception of M2M through models. It could simply be the `on` field. The base models don't have this requirement.
2. `base_manager_name` in the meta options must be specified, and it should be generated manager without an initial queryset filter.

It is thus recommended to always have these set up for all outer-join models,
in case the models will be used in relations in the future.

At the mean time, these steps must be take on the other side:

1. All related "normal" models must use the `outer_join.OuterJoinInterceptor` class so that sql generation can work correctly. It is similar to use as `OuterJoin` but only takes `queryset` argument.
2. Relations into it must have `db_constraint=False`,
because it's not referencing a real table.

See [`test04`](tests/test04_fk_out/models.py),
[`test05`](tests/test05_fk_in/models.py) and
[`test06`](tests/test06_fk_both/models.py) for example.

Relations in the base tables can still be set up the way they are intended.

Specifically for M2M relations,
if the relation itself doesn't require outer-join,
then a through model is not needed,
but `db_constraint` must be set to `False`.
See [`test07`](tests/test07_m2m_one/models.py) for example.

If the relation itself requires outer-join,
a through model should be manually provided.
See [`test08`](tests/test08_m2m_all/models.py) for example.

For relation fields in base models,
you can use `related_name='+'` to disable related managers.

## Implementation Details

### `SELECT` statement, without other `JOIN`s

The `FROM` table is extended into `FULL OUTER JOIN` with all base tables.

Outside of the `FROM` clause,
all columns in the outer-join model is transformed:

* If it exists in only one base model, we use the column from that model;
* If it exists in multiple models, we convert it into a `COALESCE` call
    * If `COALESCE` is in the `SELECT` clause, we also apply an alias (`AS`) so that the column name is preserved.

### `SELECT` statement, with other `JOIN`s

Django introduces `JOIN` statements in various occasions,
notably relation filters (`related_name__field`),
`select_related`, and M2M queries.

Consider this case:

```sql
FROM A INNER JOIN B
```

Where `B` is an outer-join model.

The safest, and probably only logically correct solution is to
introduce `B` as a subquery.
This way, we do not need to change anything in the outer query at all.

```sql
FROM A INNER JOIN (
    B1 FULL OUTER JOIN B0
) AS B
```

There will apparently be performance complications,
but it's the best solution without changing Django SQL generation significantly.

### `INSERT` statement (`WritableOuterJoin`)

For an `INSERT` statement,
it logically requires that the record doesn't exist in the `OUTER JOIN` result,
so it must not exist in the read-write table.
We simple pass on the statement to the read-write model.

### `UPDATE` statement (`WritableOuterJoin`)

We must first know whether an object is in the read-write table or not,
before deciding to run `INSERT` OR `UPDATE` on the object.

Whether an object exists or not is determined by querying the `on` column(s).

For objects that don't exist in the read-write table, we insert them;
otherwise we update them.

If the call is batch, we use batch insert/update.

### `DELETE` statement (`WritableOuterJoin`)

For objects that don't exist in the read-write table; we create them first;
and then we delete all the objects.

If the call is batch, we update batch insert/delete.

This might sound redundant,
but it guarantees any custom delete logic in the read-write model is applied to all objects,
which is especially important for `AbstractDeleteRecord`.
