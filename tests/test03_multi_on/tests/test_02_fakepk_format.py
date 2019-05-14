from ..models import A


def test_format():
    assert A.primary_key.format(['x', 'y']) == 'x-y'


def test_parse():
    assert A.primary_key.parse('x-y') == ['x', 'y']
