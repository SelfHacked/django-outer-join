__version__ = '0.1dev0'

try:
    from .models import (
        OuterJoinInterceptor,
        OuterJoin,
        WritableOuterJoin,
    )
except ImportError:
    pass
