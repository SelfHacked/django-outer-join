import typing as _typing

from django.db.models.sql.compiler import (
    SQLCompiler as _SQLCompiler,
    SQLInsertCompiler as _SQLInsertCompiler,
    SQLDeleteCompiler as _SQLDeleteCompiler,
    SQLUpdateCompiler as _SQLUpdateCompiler,
    SQLAggregateCompiler as _SQLAggregateCompiler,
)

from outer_join.models import (
    OuterJoin as _OuterJoin,
)
from outer_join.util import cached_property


class BaseOuterJoinSqlCompiler(_SQLCompiler):
    @cached_property
    def base_table(self) -> '_BaseTable':
        return self.query.alias_map[self.query.base_table]

    @cached_property
    def outer_join(self) -> _typing.Optional[_OuterJoin]:
        return _OuterJoin.get_instance(table_name=self.base_table.table_name)

    GLOBAL_WRAPPERS: _typing.List[
        _typing.Tuple[
            _typing.Type,
            _typing.Type['_Wrapper'],
        ]
    ] = []
    WRAPPERS: _typing.List[
        _typing.Tuple[
            _typing.Type,
            _typing.Type['_Wrapper'],
        ]
    ] = []

    def compile(self, node, select_format=False):
        for t, Wrapper in self.GLOBAL_WRAPPERS:
            if not isinstance(node, t):
                continue
            wrapper = Wrapper(node)
            return wrapper.compile(self, select_format=select_format)

        if self.outer_join is None:
            return super().compile(node, select_format=select_format)

        for t, Wrapper in self.WRAPPERS:
            if not isinstance(node, t):
                continue
            wrapper = Wrapper(node)
            return wrapper.compile(self, select_format=select_format)

        return super().compile(node, select_format=select_format)


from .wrappers import (
    Wrapper as _Wrapper,
)
from .wrappers.join import (
    _Join,
    JoinWrapper as _JoinWrapper,
)
from .wrappers.base_table import (
    _BaseTable,
    BaseTableWrapper as _BaseTableWrapper,
)
from .wrappers.column import (
    _Col,
    ColWrapper as _ColWrapper,
)
from .wrappers.lookup import (
    _Lookup,
    LookupWrapper as _LookupWrapper,
)


class SQLCompiler(BaseOuterJoinSqlCompiler):
    GLOBAL_WRAPPERS = [
        (_Join, _JoinWrapper),
    ]
    WRAPPERS = [
        (_BaseTable, _BaseTableWrapper),
        (_Col, _ColWrapper),
        (_Lookup, _LookupWrapper),
    ]

    def get_default_columns(self, *args, **kwargs) -> _typing.List[_Col]:
        result = super().get_default_columns(*args, **kwargs)
        if self.outer_join is None:
            return result

        if self.outer_join.pk is not None:
            result = [
                col
                for col in result
                if self.outer_join.pk != col.field
            ]
        return result


SQLInsertCompiler = _SQLInsertCompiler
SQLDeleteCompiler = _SQLDeleteCompiler
SQLUpdateCompiler = _SQLUpdateCompiler
SQLAggregateCompiler = _SQLAggregateCompiler
