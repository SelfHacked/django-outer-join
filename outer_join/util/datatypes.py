import typing as _typing

from gimme_cached_property import cached_property

from .typing import (
    KT as _KT,
    VT_co as _VT_co,
)


class ImmutableDict(_typing.Mapping[_KT, _VT_co]):
    DICT_TYPE = dict

    def __init__(self, *args, **kwargs):
        self.__dict = self.DICT_TYPE(*args, **kwargs)

    @cached_property
    def __repr(self):
        return repr(self.__dict)

    def __repr__(self):
        return self.__repr

    @cached_property
    def __str(self):
        return str(self.__dict)

    def __str__(self):
        return self.__str

    @cached_property
    def __items(self):
        return self.__dict.items()

    def items(self):
        return self.__items

    @cached_property
    def __keys(self):
        return self.__dict.keys()

    def keys(self):
        return self.__keys

    @cached_property
    def __values(self):
        return self.__dict.values()

    def values(self):
        return self.__values

    @cached_property
    def __len(self):
        return len(self.__dict)

    def __len__(self) -> int:
        return self.__len

    @cached_property
    def __hash(self):
        return hash(tuple(self.__items))

    def __hash__(self):
        return self.__hash

    def __contains__(self, k: _KT):
        return k in self.__dict

    def __getitem__(self, k: _KT) -> _VT_co:
        return self.__dict[k]

    def get(self, k: _KT) -> _typing.Optional[_VT_co]:
        return self.__dict.get(k)

    def __iter__(self) -> _typing.Iterator:
        return iter(self.__dict)
