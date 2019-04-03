import typing as _typing

import django.db.models as _models
from django.db.models.base import (
    ModelBase as _ModelBase,
)
from django.db.models.expressions import (
    Col as _Col,
)
from django.db.models.options import (
    Options as _Options,
)
from django.forms import (
    model_to_dict as _model_to_dict,
)
from gimme_cached_property import cached_property
from returns import (
    returns as _returns,
)

from .datatypes import (
    ImmutableDict as _ImmutableDict,
)
from .. import (
    errors as _errors,
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
    @_returns(_ImmutableDict)
    def __field_name_to_field(self) -> _typing.Mapping[str, 'FieldInfo']:
        for field in self.fields:
            yield field.name, field

    @cached_property
    @_returns(_ImmutableDict)
    def __db_column_to_field(self) -> _typing.Mapping[str, 'FieldInfo']:
        for field in self.fields:
            yield field.column, field

    def get_field(
            self,
            *,
            name: str = None,
            column: str = None,
    ) -> 'FieldInfo':
        if name is None and column is None:
            raise ValueError

        if name is not None and column is not None:
            field = self.get_field(name=name)
            if field.column != column:
                raise _errors.FieldDoesNotExist(name=name, column=column)
            return field

        if name is not None:
            try:
                return self.__field_name_to_field[name]
            except KeyError:
                raise _errors.FieldDoesNotExist(name=name) from None

        try:
            return self.__db_column_to_field[column]
        except KeyError:
            raise _errors.FieldDoesNotExist(column=column) from None

    @_returns(_ImmutableDict)
    def to_dict(
            self,
            obj: _typing.Union[_typing.Mapping[str, _typing.Any], _models.Model],
            *,
            fields: _typing.Collection[str] = None,
            keep_none: bool = True,
            raise_unknown_field: bool = True,
    ) -> _typing.Mapping[str, _typing.Any]:
        if isinstance(obj, _models.Model):
            obj = _model_to_dict(obj)

        for k, v in obj.items():
            if fields is not None and k not in fields:
                continue
            if not keep_none and v is None:
                continue
            try:
                field = self.get_field(name=k)
            except _errors.FieldDoesNotExist:
                if not raise_unknown_field:
                    continue
                raise
            if field.is_fk and isinstance(v, _models.Model):
                v = v.pk
            yield field.column, v


class FieldInfo(object):
    def __init__(
            self,
            field: _models.Field,
            *,
            model: ModelInfo = None,
    ):
        self.__raw = field
        if model is None:
            model = ModelInfo(field.model)
        self.__model = model

    def __eq__(self, other):
        if isinstance(other, FieldInfo):
            return self == other.raw
        if not isinstance(other, _models.Field):
            return False

        raw = self.raw
        if raw == other:
            return True

        if self.model != other.model:
            return False
        if raw.name != other.name:
            return False

        return True

    @property
    def raw(self) -> _models.Field:
        return self.__raw

    @property
    def model(self) -> ModelInfo:
        return self.__model

    @property
    def column(self) -> str:
        return self.raw.column

    @property
    def name(self) -> str:
        return self.raw.name

    @cached_property
    def sql(self) -> str:
        return f'"{self.model.table_name}"."{self.column}"'

    @cached_property
    def is_fk(self) -> bool:
        return isinstance(self.raw, _models.ForeignKey)

    @property
    def col(self) -> _Col:
        return _Col(self.model.table_name, self.raw)

    @staticmethod
    def coalesce(
            field: 'FieldInfo',  # at least one must be provided
            *fields: 'FieldInfo',
    ) -> str:
        sql = 'COALESCE('
        sql += ', '.join(
            field.sql
            for field in (field, *fields)
        )
        sql += ')'
        return sql
