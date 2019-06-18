import typing as _typing
from functools import (
    lru_cache as _lru_cache,
)

import django.db.models as _models
from django.db.models.query_utils import (
    DeferredAttribute as _DeferredAttribute,
)
from returns import (
    returns as _returns,
)

from outer_join.errors import (
    FieldDoesNotExist as _FieldDoesNotExist,
    MultiplePKDeclared as _MultiplePKDeclared,
)
from outer_join.extra.fake_pk import (
    hyphen_join as _hyphen_join,
    hyphen_split as _hyphen_split,
)
from outer_join.info import (
    ModelInfo as _ModelInfo,
    FieldInfo as _FieldInfo,
)
from outer_join.typing import (
    T as _T,
)
from outer_join.util import cached_property
from outer_join.util.queryset import (
    initial_queryset as _initial_queryset,
    QuerySetFilter as _QuerySetFilter,
    QuerySetSplit as _QuerySetSplit,
)


class OuterJoinInterceptor(object):
    @staticmethod
    def _to_sequence(
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
            *,
            queryset: _typing.Type[_models.QuerySet] = None,
    ):
        self.__model: _ModelInfo = None
        self.__queryset_class = queryset

    @property
    def model(self) -> _ModelInfo:
        return self.__model

    def contribute_to_class(self, model, *args, **kwargs):
        self.__model = _ModelInfo(model)

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
        filter_initial_queryset = self._to_sequence(filter_initial_queryset, allow_none=True)

        @_initial_queryset(*filter_initial_queryset)
        class OuterJoinModelManager(_models.Manager.from_queryset(outer_join._queryset_class)):
            pass

        return OuterJoinModelManager


class OuterJoin(OuterJoinInterceptor):
    __ALL: _typing.List['OuterJoin'] = []

    @classmethod
    def get_instance(
            cls,
            *,
            model: _typing.Type[_models.Model] = None,
            table_name: str = None,
    ) -> _typing.Optional['OuterJoin']:
        for instance in cls.__ALL:
            if model is not None and instance.model != model:
                continue
            if table_name is not None and table_name != instance.model.table_name:
                continue
            return instance
        return None

    def __init__(
            self,
            first: _typing.Type[_models.Model],  # at least one must be provided
            *base_models: _typing.Type[_models.Model],
            on: _typing.Union[str, _typing.Sequence[str]],
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.__base_models = tuple((
            _ModelInfo(model)
            for model in (first, *base_models)
        ))
        self.__on = self._to_sequence(on, allow_none=False)
        self.__pk = None

    @property
    def base_models(self) -> _typing.Sequence[_ModelInfo]:
        return self.__base_models

    @property
    def first(self) -> _ModelInfo:
        return self.base_models[0]

    @property
    def on(self) -> _typing.Sequence[str]:
        return self.__on

    def get_primary_key(
            self,
            base_class: _typing.Type[_models.Field] = _models.TextField,
            *,
            format_pk: _typing.Callable[[_typing.Iterable], str] = _hyphen_join,
            parse_pk: _typing.Callable[[str], _typing.Iterable] = _hyphen_split,
    ) -> _typing.Type[_models.Field]:
        outer_join = self

        def set_pk(field):
            if outer_join.pk is None:
                outer_join.__pk = _FieldInfo(field)
                return
            if outer_join.pk == field:
                return
            raise _MultiplePKDeclared

        class PKField(base_class):
            def __init__(self, *args, **kwargs):
                kwargs['primary_key'] = True
                super().__init__(*args, **kwargs)
                self.__format_pk = format_pk
                self.__parse_pk = parse_pk

            @property
            def format_pk(self):
                return self.__format_pk

            @property
            def parse_pk(self):
                return self.__parse_pk

            @cached_property
            def _deferred_attribute_class(self):
                field = self

                class PKDeferredAttribute(object):
                    def __get__(self, instance, cls=None):
                        if instance is None:
                            return self
                        return field.format_pk((
                            getattr(instance, outer_join.model.get_field(name=on).attr)
                            for on in outer_join.on
                        ))

                    @property
                    def format(self):
                        return field.format_pk

                    @property
                    def parse(self):
                        return field.parse_pk

                return PKDeferredAttribute

            def contribute_to_class(self, model, name, *args, **kwargs):
                super().contribute_to_class(model, name, *args, **kwargs)
                if isinstance(getattr(model, self.attname), _DeferredAttribute):
                    # replace the deferred attribute
                    setattr(model, self.attname, self._deferred_attribute_class())
                set_pk(self)

            @classmethod
            @_lru_cache(maxsize=None)
            def get_lookups(cls):
                result = super().get_lookups()
                return {
                    'exact': result['exact'],
                }

            def deconstruct(self):
                module = self.__class__.__module__
                qualname = self.__class__.__qualname__
                try:
                    # use `path` from base class
                    self.__class__.__module__ = base_class.__module__
                    self.__class__.__qualname__ = base_class.__qualname__
                    return super().deconstruct()
                finally:
                    self.__class__.__module__ = module
                    self.__class__.__qualname__ = qualname

        return PKField

    @property
    def pk(self) -> _FieldInfo:
        return self.__pk

    def contribute_to_class(self, model, *args, **kwargs):
        super().contribute_to_class(model, *args, **kwargs)
        if self.get_instance(model=model) is None:
            # only store the first
            self.__ALL.append(self)

    @cached_property
    def outer_join_from(self) -> str:
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
    def get_fields(self, name: str) -> _typing.Sequence[_FieldInfo]:
        for model in self.base_models:
            try:
                yield model.get_field(name=name)
            except _FieldDoesNotExist:
                continue


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
                # Note: the `bulk_create` method may be customized in the writable table.
                # See `AbstractDeleteRecord`.
                write_objs = [
                    model(**d)
                    for d in rw.to_dicts(objs, keep_none=False)
                ]
                model._default_manager.bulk_create(write_objs, batch_size=batch_size)
                return objs

            def update(self, **kwargs):
                split = _QuerySetSplit(self, rw, *outer_join.on)
                split.get_existing_queryset().update(**kwargs)
                split.bulk_create_new(**kwargs)
                # clear cache
                self._result_cache = None

            def delete(self):
                split = _QuerySetSplit(self, rw, *outer_join.on)
                split.bulk_create_new()
                # now that new ones are created, we use split again to get the full queryset
                split = _QuerySetSplit(self, rw, *outer_join.on)
                split.get_existing_queryset().delete()
                # clear cache
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
