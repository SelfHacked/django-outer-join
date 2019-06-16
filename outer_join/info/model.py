import typing as _typing

import django.db.models as _models
from django.db.models.base import (
    ModelBase as _ModelBase,
)
from django.db.models.options import (
    Options as _Options,
)
from django.forms import (
    model_to_dict as _model_to_dict,
)
from returns import (
    returns as _returns,
)

from outer_join.errors import (
    FieldDoesNotExist as _FieldDoesNotExist,
)
from outer_join.util import cached_property
from outer_join.util.datatypes import (
    ImmutableDict as _ImmutableDict,
)


class ModelInfo(object):
    def __init__(self, model: _typing.Type[_models.Model]):
        self.__raw = model

    def __eq__(self, other):
        if isinstance(other, ModelInfo):
            return self == other.raw
        if not isinstance(other, (_models.Model, _ModelBase)):
            return False

        raw = self.raw
        if raw == other:
            return True

        if raw._meta.label != other._meta.label:
            return False

        return True

    @property
    def raw(self) -> _typing.Type[_models.Model]:
        return self.__raw

    @property
    def meta(self) -> _Options:
        return self.raw._meta

    @property
    def table_name(self) -> str:
        return self.meta.db_table

    @cached_property
    @_returns(tuple)
    def fields(self) -> _typing.Sequence['FieldInfo']:
        for field in self.meta.fields:
            yield FieldInfo(field, model=self)

    @cached_property
    def _field_finders(self):
        return ModelFieldFinders(
            name=NameModelFieldFinder(self),
            attr=AttributeModelFieldFinder(self, 'attr'),
            column=AttributeModelFieldFinder(self, 'column'),
        )

    def get_field(
            self,
            *,
            name: str = None,
            attr: str = None,
            column: str = None,
    ) -> 'FieldInfo':
        return self._field_finders.get(
            name=name,
            attr=attr,
            column=column,
        )

    FieldValueDict = _typing.Mapping[str, _typing.Any]
    Object = _typing.Union[FieldValueDict, _models.Model]

    @cached_property
    def pk(self) -> 'FieldInfo':
        return FieldInfo(self.meta.pk)

    @_returns(_ImmutableDict)
    def to_dict(
            self,
            obj: Object,
            *,
            fields: _typing.Collection[str] = None,
            keep_none: bool = True,
            raise_unknown_field: bool = True,
    ) -> FieldValueDict:
        if isinstance(obj, _models.Model):
            obj = _model_to_dict(obj)

        if fields is not None and 'pk' in fields:
            fields = [
                *fields,
                self.pk.name,
            ]

        for k, v in obj.items():
            if fields is not None and k not in fields:
                continue
            if not keep_none and v is None:
                continue
            try:
                field = self.get_field(name=k)
            except _FieldDoesNotExist:
                if not raise_unknown_field:
                    continue
                raise
            if field.is_fk and isinstance(v, _models.Model):
                v = v.pk
            yield field.attr, v

    Objects = _typing.Union[_typing.Iterable[Object], _models.QuerySet]

    def to_dicts(
            self,
            objs: Objects,
            *,
            fields: _typing.Collection[str] = None,
            keep_none: bool = True,
            raise_unknown_field: bool = True,
    ) -> _typing.Iterator[FieldValueDict]:
        if isinstance(objs, _models.QuerySet):
            objs = objs.values(*fields).iterator()
        for obj in objs:
            yield self.to_dict(
                obj,
                fields=fields,
                keep_none=keep_none,
                raise_unknown_field=raise_unknown_field,
            )


from .field import FieldInfo
from .field_lookup import (
    ModelFieldFinders,
    AttributeModelFieldFinder,
    NameModelFieldFinder,
)
