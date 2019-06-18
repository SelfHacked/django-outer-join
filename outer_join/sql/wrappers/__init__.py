import typing as _typing

from outer_join.typing import (
    T as _T,
)


class Wrapper(_typing.Generic[_T]):
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def compile(
            self,
            compiler: '_BaseOuterJoinSqlCompiler',
            *,
            select_format,
    ):
        return self.as_sql(compiler, compiler.connection)

    def as_sql(self, compiler, connection):
        return self.wrapped.as_sql(compiler, connection)


from ..compiler import (
    BaseOuterJoinSqlCompiler as _BaseOuterJoinSqlCompiler,
)
