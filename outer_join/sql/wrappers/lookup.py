from django.db.models import (
    Lookup as _Lookup,
)
from django.db.models.expressions import (
    Col as _Col,
)
from django.db.models.lookups import (
    Exact as _Exact,
)

from . import (
    Wrapper as _Wrapper,
)


class LookupWrapper(_Wrapper[_Lookup]):
    def compile(self, compiler, *, select_format):
        if compiler.outer_join.pk is None:
            return super().compile(compiler, select_format=select_format)
        if not isinstance(self.wrapped.lhs, _Col):
            return super().compile(compiler, select_format=select_format)

        pk = compiler.outer_join.pk.raw
        if self.wrapped.lhs.field is not pk:
            return super().compile(compiler, select_format=select_format)

        sqls = []
        params = []
        for on, val in zip(compiler.outer_join.on, pk.parse_pk(self.wrapped.rhs)):
            exact = _Exact(
                compiler.outer_join.model.get_field(name=on).col(),
                val,
            )
            sql, param = compiler.compile(exact)
            sqls.append(sql)
            params.extend(param)

        final_sql = '((' + ') AND ('.join(sqls) + '))'
        return final_sql, params
