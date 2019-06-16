from django.db.models import (
    QuerySet as _QuerySet,
)

from outer_join.util.queryset import (
    QuerySetFilter as _QuerySetFilter,
)


def filter_field(field: str, val) -> _QuerySetFilter:
    def __filter(queryset: _QuerySet) -> _QuerySet:
        return queryset.filter(**{field: val})

    return __filter


def exclude_field(field: str, val) -> _QuerySetFilter:
    def __filter(queryset: _QuerySet) -> _QuerySet:
        return queryset.exclude(**{field: val})

    return __filter


def filter_exact(field: str, val) -> _QuerySetFilter:
    def __filter(queryset: _QuerySet) -> _QuerySet:
        return queryset.filter(**{f"{field}__exact": val})

    return __filter


def exclude_exact(field: str, val) -> _QuerySetFilter:
    def __filter(queryset: _QuerySet) -> _QuerySet:
        return queryset.exclude(**{f"{field}__exact": val})

    return __filter


def filter_null(field: str) -> _QuerySetFilter:
    def __filter(queryset: _QuerySet) -> _QuerySet:
        return queryset.filter(**{f"{field}__isnull": True})

    return __filter


def exclude_null(field: str) -> _QuerySetFilter:
    def __filter(queryset: _QuerySet) -> _QuerySet:
        return queryset.exclude(**{f"{field}__isnull": True})

    return __filter
