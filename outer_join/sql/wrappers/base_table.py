from django.db.models.sql.datastructures import (
    BaseTable as _BaseTable,
)

from . import (
    Wrapper as _Wrapper,
)


class BaseTableWrapper(_Wrapper[_BaseTable]):
    def compile(self, compiler, *, select_format):
        if compiler.outer_join.model.table_name != self.wrapped.table_name:
            return super().compile(compiler, select_format=select_format)

        return compiler.outer_join.outer_join_from, []
