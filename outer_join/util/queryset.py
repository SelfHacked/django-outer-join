import typing as _typing
from django.db.models import (
    QuerySet as _QuerySet,
)
from django.db.models.manager import (
    BaseManager as _BaseManager,
)
from functools import (
    wraps as _wraps,
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
