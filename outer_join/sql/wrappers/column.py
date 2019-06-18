from django.db.models.expressions import (
    Col as _Col,
)

from outer_join.errors import (
    JoinFieldError as _JoinFieldError,
)
from outer_join.info import (
    FieldInfo as _FieldInfo,
)
from . import (
    Wrapper as _Wrapper,
)


class ColWrapper(_Wrapper[_Col]):
    def compile(self, compiler, *, select_format):
        field = self.wrapped.target
        if compiler.outer_join.model != field.model:
            return super().compile(compiler, select_format=select_format)

        name = field.name
        fields = compiler.outer_join.get_fields(name)
        if len(fields) == 0:
            raise _JoinFieldError(compiler.outer_join.model, name)

        if len(fields) == 1:
            return compiler.compile(fields[0].col, select_format=select_format)

        sql = _FieldInfo.coalesce(*fields)
        if select_format:
            column = compiler.outer_join.model.get_field(name=name).column
            sql += f' AS {column}'
        return sql, []
