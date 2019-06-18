from django.db.models.sql.datastructures import (
    Join as _Join,
)

from outer_join.models import (
    OuterJoin as _OuterJoin,
)
from . import (
    Wrapper as _Wrapper,
)


class JoinWrapper(_Wrapper[_Join]):
    def compile(self, compiler, *, select_format):
        left_instance = _OuterJoin.get_instance(table_name=self.wrapped.parent_alias)
        right_instance = _OuterJoin.get_instance(table_name=self.wrapped.table_name)
        if left_instance is None and right_instance is None:
            return super().compile(compiler, select_format=select_format)

        join_conditions = []
        params = []

        # Add a join condition for each pair of joining columns.
        for index, (lhs_col, rhs_col) in enumerate(self.wrapped.join_cols):
            if left_instance is None:
                left = f'"{self.wrapped.parent_alias}"."{lhs_col}"'
            else:
                left, lp = compiler.compile(
                    left_instance.model.get_field(column=lhs_col).col,
                    select_format=False,
                )
                params.extend(lp)
            right = f'"{self.wrapped.table_alias}"."{rhs_col}"'
            join_conditions.append(f"{left} = {right}")

        # Add a single condition inside parentheses for whatever
        # get_extra_restriction() returns.
        extra_cond = self.wrapped.join_field.get_extra_restriction(
            compiler.query.where_class, self.wrapped.table_alias, self.wrapped.parent_alias)
        if extra_cond:
            extra_sql, extra_params = compiler.compile(extra_cond)
            join_conditions.append('(%s)' % extra_sql)
            params.extend(extra_params)
        if self.wrapped.filtered_relation:
            extra_sql, extra_params = compiler.compile(self.wrapped.filtered_relation)
            if extra_sql:
                join_conditions.append('(%s)' % extra_sql)
                params.extend(extra_params)
        if not join_conditions:
            # This might be a rel on the other end of an actual declared field.
            declared_field = getattr(self.wrapped.join_field, 'field', self.wrapped.join_field)
            raise ValueError(
                "Join generated an empty ON clause. %s did not yield either "
                "joining columns or extra restrictions." % declared_field.__class__
            )
        on_clause_sql = ' AND '.join(join_conditions)

        sql = f'{self.wrapped.join_type} '
        if right_instance is not None:
            subquery = right_instance.model.raw._default_manager.all().query
            sql += f'({subquery}) AS '
        sql += f'{self.wrapped.table_name} ON ({on_clause_sql})'
        return sql, params
