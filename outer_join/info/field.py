import django.db.models as _models
from django.db.models.expressions import (
    Col as _Col,
)
from gimme_cached_property import cached_property


class FieldInfo(object):
    def __init__(
            self,
            field: _models.Field,
            *,
            model: 'ModelInfo' = None,
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
    def model(self) -> 'ModelInfo':
        return self.__model

    @property
    def column(self) -> str:
        return self.raw.column

    @property
    def attr(self) -> str:
        return self.raw.attname

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


from .model import ModelInfo
