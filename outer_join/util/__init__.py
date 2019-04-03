import typing as _typing
from functools import (
    wraps as _wraps,
)

from django.utils.functional import (
    cached_property as _cached_property,
)

from .typing import (
    T as _T,
)

# PyCharm doesn't like aliases for cached_property, so we unify import from here
# Avoid cleanup import by PyCharm
cached_property = _cached_property


class returns(object):
    """
    This code can be found in selfhacked-util
    However it's the only thing we need from the package,
    so we are copying the code here and getting rid of the dependency.
    """

    def __init__(self, type: _typing.Type[_T]):
        self.__type = type

    def __call__(self, func) -> _T:
        @_wraps(func)
        def __new_func(*args, **kwargs):
            return self.__type(func(*args, **kwargs))

        return __new_func
