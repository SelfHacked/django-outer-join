from typing import TypeVar as _TypeVar

T = _TypeVar('T')  # Any type.
KT = _TypeVar('KT')  # Key type.
VT_co = _TypeVar('VT_co', covariant=True)  # Value type covariant containers.
