from django.db.models.expressions import (
    Col as _Col,
)
from django.db.models.functions import (
    Coalesce as _Coalesce,
)

from outer_join.errors import (
    JoinFieldError as _JoinFieldError,
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

        coalesce = _Coalesce(*(field.col for field in fields))
        sql, params = coalesce.as_sql(compiler, compiler.connection)
        if select_format:
            column = compiler.outer_join.model.get_field(name=name).column
            sql += f' AS {column}'
        return sql, []
