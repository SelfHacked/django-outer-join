from django.utils.functional import (
    cached_property as _cached_property,
)

cached_property = _cached_property

# PyCharm doesn't like aliases for cached_property, so we unify import from here
# Avoid cleanup import by PyCharm
