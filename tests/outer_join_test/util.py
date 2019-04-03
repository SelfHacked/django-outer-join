import django
import pytest

skip_2_2_related_manager = pytest.mark.skipif(
    django.VERSION >= (2, 2),
    reason='New related manager behavior in 2.2 not yet supported',
)
