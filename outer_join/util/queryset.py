import typing as _typing
from functools import (
    wraps as _wraps,
)

from django.db.models import (
    QuerySet as _QuerySet,
    Model as _Model,
)
from django.db.models.manager import (
    BaseManager as _BaseManager,
    Manager as _Manager,
)
from gimme_cached_property import cached_property
from returns import (
    returns as _returns,
)

from .info import (
    ModelInfo as _ModelInfo,
)

QuerySetFilter = _typing.Callable[[_QuerySet], _QuerySet]


def initial_queryset(*funcs: QuerySetFilter):
    """
    Decorate the `get_queryset` method of a manager, or the manager itself

    :param funcs:
        (queryset) -> queryset function
    """
    if len(funcs) == 0:
        return lambda x: x

    def __decor(get_queryset):
        if isinstance(get_queryset, type) and issubclass(get_queryset, _BaseManager):
            # if decorating Manager
            get_queryset.get_queryset = __decor(get_queryset.get_queryset)
            return get_queryset

        @_wraps(get_queryset)
        def __new_get_queryset(self):
            queryset = get_queryset(self)
            for func in funcs:
                queryset = func(queryset)
            return queryset

        return __new_get_queryset

    return __decor


class QuerySetSplit(object):
    """
    Using a a set of objects or a queryset from a model A,
    query another model B and determine which ones exist in B and which ones don't,
    by looking up specific fields.
    """

    def __init__(
            self,
            objects: _ModelInfo.Objects,
            model: _typing.Union[_ModelInfo, _typing.Type[_Model]],
            *on: str,
            manager: _typing.Union[str, _Manager] = '_default_manager',
    ):
        self.__objects = objects
        if not isinstance(model, _ModelInfo):
            model = _ModelInfo(model)
        self.__model_info = model
        self.__on = tuple(on)
        self.__manager = manager

    @property
    def objects(self) -> _ModelInfo.Objects:
        return self.__objects

    @property
    def model_info(self) -> _ModelInfo:
        return self.__model_info

    @property
    def model(self) -> _typing.Type[_Model]:
        return self.model_info.raw

    @property
    def manager(self) -> _Manager:
        if isinstance(self.__manager, str):
            return getattr(self.model, self.__manager)
        return self.__manager

    @property
    def on(self) -> _typing.Sequence[str]:
        return self.__on

    OnFieldValueSet = _typing.Set[_ModelInfo.FieldValueDict]

    @cached_property
    @_returns(set)
    def all(self) -> OnFieldValueSet:
        yield from self.model_info.to_dicts(
            self.objects,
            fields=self.on,
        )

    @cached_property
    def _existing(self) -> _typing.Tuple[OnFieldValueSet, set]:
        existing = set()
        existing_pks = set()

        # filter fields individually
        # e.g.
        # instead of {(a, b) in [(1, 1), (2, 2)]}
        # we first filter {a in [1, 2] and b in [1, 2]}
        query = {
            f"{on}__in": {item[self.model_info.get_field(name=on).column] for item in self.all}
            for on in self.on
        }
        qs: _QuerySet = self.manager.filter(**query)

        # next we need to match them against all fields
        for obj in qs.iterator():
            obj_id = self.model_info.to_dict(obj, fields=self.on)
            if obj_id not in self.all:
                continue
            existing.add(obj_id)
            existing_pks.add(obj.pk)

        return existing, existing_pks

    @property
    def existing(self) -> OnFieldValueSet:
        return self._existing[0]

    @property
    def existing_pks(self) -> set:
        return self._existing[1]

    def get_existing_queryset(self) -> _QuerySet:
        return self.manager.filter(pk__in=self.existing_pks)

    @cached_property
    def new(self) -> OnFieldValueSet:
        return self.all - self.existing

    def bulk_create_new(self, **kwargs):
        return self.manager.bulk_create([
            self.model(
                **obj_id,
                **kwargs,
            )
            for obj_id in self.new
        ])
