import django.db.models as _models
import typing as _typing
from django.db import (
    connections as _connections,
)
from django.db.models.expressions import (
    Col as _Col,
)
from django.db.models.sql import (
    Query as _Query,
)
from django.db.models.sql.compiler import (
    SQLCompiler as _SQLCompiler,
)
from django.db.models.sql.datastructures import (
    BaseTable as _BaseTable,
    Join as _Join,
)

from .util import (
    cached_property,
    returns as _returns,
)
from .util.info import (
    ModelInfo as _ModelInfo,
    FieldInfo as _FieldInfo,
)
from .util.queryset import (
    initial_queryset as _initial_queryset,
    QuerySetFilter as _QuerySetFilter,
)
from .util.typing import (
    T as _T,
)


class OuterJoin(object):
    __ALL: _typing.List['OuterJoin'] = []

    @classmethod
    def get_instance(
            cls,
            *,
            model: _typing.Type[_models.Model] = None,
            table_name: str = None,
    ) -> _typing.Optional['OuterJoin']:
        for instance in cls.__ALL:
            if model is not None and model is not instance.model.raw:
                continue
            if table_name is not None and table_name != instance.model.table_name:
                continue
            return instance
        return None

    class JoinFieldError(Exception):
        def __init__(self, model: _ModelInfo, name: str):
            msg = f"Field {model.raw.__name__}.{name} does not exist in any base model"
            super().__init__(msg)
            self.model = model
            self.name = name

    @staticmethod
    def __to_sequence(
            item: _typing.Union[_T, _typing.Sequence[_T], None],
            *,
            allow_none: bool,
    ) -> _typing.Sequence[_T]:
        if item is None:
            if not allow_none:
                raise ValueError
            return ()
        if isinstance(item, str):
            return item,  # tuple
        try:
            len(item)
        except TypeError:
            return item,  # tuple
        else:
            return tuple(item)

    def __init__(
            self,
            first: _typing.Type[_models.Model],  # at least one must be provided
            *base_models: _typing.Type[_models.Model],
            queryset: _typing.Type[_models.QuerySet] = None,
            on: _typing.Union[str, _typing.Sequence[str]],
    ):
        self.__model: _ModelInfo = None
        self.__base_models = tuple((
            _ModelInfo(model)
            for model in (first, *base_models)
        ))
        self.__queryset_class = queryset
        self.__on = self.__to_sequence(on, allow_none=False)

    @property
    def model(self) -> _ModelInfo:
        return self.__model

    @property
    def base_models(self) -> _typing.Sequence[_ModelInfo]:
        return self.__base_models

    @property
    def first(self) -> _ModelInfo:
        return self.base_models[0]

    @property
    def on(self) -> _typing.Sequence[str]:
        return self.__on

    def contribute_to_class(self, model, *args, **kwargs):
        self.__model = _ModelInfo(model)
        if self.get_instance(model=model) is None:
            # only store the first
            self.__ALL.append(self)

    @cached_property
    def _outer_join_from(self) -> str:
        sql = f'"{self.first.table_name}"'
        for model in self.base_models[1:]:
            sql += f' FULL OUTER JOIN "{model.table_name}" ON ('
            sql += ' AND '.join(
                f'{self.first.get_field(name=on).sql} = {model.get_field(name=on).sql}'
                for on in self.on
            )
            sql += ')'
        return sql

    @_returns(tuple)
    def _get_fields(self, name: str) -> _typing.Sequence['_FieldInfo']:
        for model in self.base_models:
            try:
                yield model.get_field(name=name)
            except _ModelInfo.FieldDoesNotExist:
                continue

    @cached_property
    def _compiler_class(self) -> _typing.Type[_SQLCompiler]:
        outer_join = self

        class OuterJoinSqlCompiler(_SQLCompiler):
            def _compile_base_table(self, node: _BaseTable, *, select_format):
                if node.table_name != outer_join.model.table_name:
                    return super().compile(node, select_format=select_format)

                return outer_join._outer_join_from, []

            def _compile_join(self, node: _Join, *, select_format):
                left_instance = outer_join.get_instance(table_name=node.parent_alias)
                right_instance = outer_join.get_instance(table_name=node.table_name)
                if left_instance is None and right_instance is None:
                    return super().compile(node, select_format=select_format)

                params = []
                sql = f'{node.join_type} '
                if right_instance is not None:
                    subquery = right_instance.model.raw._default_manager.all().query
                    sql += f'({subquery}) AS '
                sql += f'{node.table_name} ON ('

                def __conditions(self, compiler):
                    """Copied from Join.as_sql and modified according to left_instance"""

                    join_conditions = []

                    # Add a join condition for each pair of joining columns.
                    for index, (lhs_col, rhs_col) in enumerate(self.join_cols):
                        if left_instance is None:
                            left = f'"{self.parent_alias}"."{lhs_col}"'
                        else:
                            left, lp = compiler._compile_col(
                                left_instance.model.get_field(column=lhs_col).col,
                                select_format=False,
                            )
                            params.extend(lp)
                        right = f'"{self.table_alias}"."{rhs_col}"'
                        join_conditions.append(f"{left} = {right}")

                    # Add a single condition inside parentheses for whatever
                    # get_extra_restriction() returns.
                    extra_cond = self.join_field.get_extra_restriction(
                        compiler.query.where_class, self.table_alias, self.parent_alias)
                    if extra_cond:
                        extra_sql, extra_params = compiler.compile(extra_cond)
                        join_conditions.append('(%s)' % extra_sql)
                        params.extend(extra_params)
                    if self.filtered_relation:
                        extra_sql, extra_params = compiler.compile(self.filtered_relation)
                        if extra_sql:
                            join_conditions.append('(%s)' % extra_sql)
                            params.extend(extra_params)
                    if not join_conditions:
                        # This might be a rel on the other end of an actual declared field.
                        declared_field = getattr(self.join_field, 'field', self.join_field)
                        raise ValueError(
                            "Join generated an empty ON clause. %s did not yield either "
                            "joining columns or extra restrictions." % declared_field.__class__
                        )
                    return ' AND '.join(join_conditions)

                sql += __conditions(node, self)
                sql += ') '
                return sql, params

            def _compile_col(self, node: _Col, *, select_format):
                field = node.target
                if field.model is not outer_join.model.raw:
                    return super().compile(node, select_format=select_format)

                name = field.name
                fields = outer_join._get_fields(name)
                if len(fields) == 0:
                    raise outer_join.JoinFieldError(outer_join.model, name)

                if len(fields) == 1:
                    return super().compile(fields[0].col, select_format=select_format)

                sql = _FieldInfo.coalesce(*fields)
                if select_format:
                    sql += f' AS {outer_join.model.get_field(name=name).column}'
                return sql, []

            def compile(self, node, select_format=False):
                if isinstance(node, _BaseTable):
                    return self._compile_base_table(node, select_format=select_format)
                elif isinstance(node, _Join):
                    return self._compile_join(node, select_format=select_format)
                elif isinstance(node, _Col):
                    return self._compile_col(node, select_format=select_format)
                return super().compile(node, select_format=select_format)

        return OuterJoinSqlCompiler

    @cached_property
    def _query_class(self) -> _typing.Type[_Query]:
        outer_join = self

        class OuterJoinQuery(_Query):
            def get_compiler(self, using=None, connection=None):
                if using is None and connection is None:
                    raise ValueError("Need either using or connection")
                if using:
                    connection = _connections[using]
                return outer_join._compiler_class(
                    self,
                    connection,
                    using,
                )

        return OuterJoinQuery

    def _get_query(self, *args, **kwargs) -> _Query:
        return self._query_class(self.model.raw, *args, **kwargs)

    @property
    def _queryset_class(self) -> _typing.Type[_models.QuerySet]:
        if self.__queryset_class is None:
            return _models.QuerySet
        return self.__queryset_class

    def get_manager(
            self,
            *,
            filter_initial_queryset: _typing.Union[
                _QuerySetFilter,
                _typing.Sequence[_QuerySetFilter],
                None,
            ] = None,
    ) -> _typing.Type[_models.Manager]:
        """
        :param filter_initial_queryset:
            A QuerySetFilter,
            a sequence of them (list or tuple),
            or None
        """
        outer_join = self
        filter_initial_queryset = self.__to_sequence(filter_initial_queryset, allow_none=True)

        class OuterJoinModelManager(_models.Manager.from_queryset(outer_join._queryset_class)):
            @_initial_queryset(*filter_initial_queryset)
            def get_queryset(self):
                queryset = self._queryset_class(
                    query=outer_join._get_query(),
                    model=self.model,
                    using=self._db,
                    hints=self._hints,
                )
                return queryset

        return OuterJoinModelManager


class WritableOuterJoin(OuterJoin):
    def __init__(
            self,
            rw_model: _typing.Type[_models.Model],
            *readonly_models: _typing.Type[_models.Model],
            **kwargs,
    ):
        self.__rw_model = rw_model
        super().__init__(rw_model, *readonly_models, **kwargs)

    @property
    def rw_model(self) -> _typing.Type[_models.Model]:
        return self.__rw_model

    @property
    def rw(self) -> _ModelInfo:
        return self.first

    def contribute_to_class(self, model, *args, **kwargs):
        super().contribute_to_class(model, *args, **kwargs)
        model.save = self._save_method
        model.delete = self._delete_method

    @cached_property
    def _queryset_class(self) -> _typing.Type[_models.QuerySet]:
        queryset_class = super()._queryset_class
        outer_join = self
        model = outer_join.rw_model
        rw = outer_join.rw

        class WritableOuterJoinQuerySet(queryset_class):
            def bulk_create(self, objs, batch_size=None):
                # just create because if something's not in OUTER JOIN, it's not in writable table
                clean_dicts = (
                    rw.to_dict(obj, keep_none=False)
                    for obj in objs
                )
                write_objs = [
                    model(**d)
                    for d in clean_dicts
                ]
                model._default_manager.bulk_create(write_objs, batch_size=batch_size)
                return objs

            @property
            @_returns(set)
            def rw_all_ids(self) -> set:
                for item in self.values(*outer_join.on).iterator():
                    yield rw.to_dict(item)

            def rw_split(self) -> _typing.Tuple[set, set, set, _models.QuerySet]:
                all_ids = self.rw_all_ids
                existing_ids = set()
                existing_pks = set()

                existing_query = {
                    f"{on}__in": {item[rw.get_field(name=on).column] for item in all_ids}
                    for on in outer_join.on
                }
                existing: _models.QuerySet = model._default_manager.filter(**existing_query)
                # here we only filtered fields individually
                # next we need to match them against all fields
                for obj in existing.iterator():
                    obj_id = rw.to_dict(obj, fields=outer_join.on)
                    if obj_id not in all_ids:
                        continue
                    existing_ids.add(obj_id)
                    existing_pks.add(obj.pk)

                new_ids = all_ids - existing_ids
                existing_queryset = model._default_manager.filter(pk__in=existing_pks)

                return all_ids, existing_ids, new_ids, existing_queryset

            def update(self, **kwargs):
                # we need to know which ones exist in the writable table, and which ones don't
                all_ids, existing_ids, new_ids, existing = self.rw_split()

                existing.update(**kwargs)

                model._default_manager.bulk_create([
                    model(
                        **obj_id,
                        **kwargs,
                    )
                    for obj_id in new_ids
                ])

                # clear cache
                self._result_cache = None

            def delete(self):
                new_ids = self.rw_split()[2]

                model._default_manager.bulk_create([
                    model(**obj_id)
                    for obj_id in new_ids
                ])

                existing = self.rw_split()[3]
                existing.delete()

                self._result_cache = None

        return WritableOuterJoinQuerySet

    @cached_property
    def _save_method(self):
        outer_join = self
        model = outer_join.rw_model
        rw = outer_join.rw

        def save(obj, using=None, *args, **kwargs):
            try:
                write_obj = model._default_manager.get(**rw.to_dict(obj, fields=outer_join.on))
            except model.DoesNotExist:
                # create new
                write_obj = model(**rw.to_dict(obj, keep_none=False, raise_unknown_field=False))
            else:
                for k, v in rw.to_dict(obj, raise_unknown_field=False).items():
                    setattr(write_obj, k, v)
            write_obj.save(using=using, *args, **kwargs)

            # update state of object
            obj._state.db = using
            obj._state.adding = False

        return save

    @cached_property
    def _delete_method(self):
        outer_join = self
        model = outer_join.rw_model
        rw = outer_join.rw

        def delete(obj, *args, **kwargs):
            obj_id = rw.to_dict(obj, fields=outer_join.on)
            try:
                write_obj = model._default_manager.get(**obj_id)
            except model.DoesNotExist:
                # create new
                # We will call .delete() for this new object,
                # because there may be special logic for delete() call in the writable model.
                # Even if there isn't, it will fail there, and it doesn't concern us here.
                write_obj = model(**obj_id)
            write_obj.delete(*args, **kwargs)

        return delete
