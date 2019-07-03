from django.db.models.sql.datastructures import (
    BaseTable as _BaseTable,
)

from outer_join.models import (
    OuterJoin as _OuterJoin,
)
from . import (
    Wrapper as _Wrapper,
)


class OuterJoinBaseTable:
    def __init__(self, outer_join: _OuterJoin):
        self.outer_join = outer_join

    def as_sql(self, compiler, connection):
        sqls = []
        params = []

        first = self.outer_join.first

        sqls.append(first.table_name)
        for model in self.outer_join.base_models[1:]:
            sqls.append(f' FULL OUTER JOIN "{model.table_name}" ON (')

            on_sqls = []
            for on in self.outer_join.on:
                sql1, param1 = compiler.compile(first.get_field(name=on).col())
                sql2, param2 = compiler.compile(model.get_field(name=on).col())
                on_sqls.append(f'{sql1} = {sql2}')
                params.extend(param1)
                params.extend(param2)

            sqls.append(' AND '.join(on_sqls))
            sqls.append(')')

        return ''.join(sqls), params


class BaseTableWrapper(_Wrapper[_BaseTable]):
    def compile(self, compiler, *, select_format):
        if compiler.outer_join.model.table_name != self.wrapped.table_name:
            return super().compile(compiler, select_format=select_format)

        return compiler.compile(OuterJoinBaseTable(compiler.outer_join), select_format=select_format)
