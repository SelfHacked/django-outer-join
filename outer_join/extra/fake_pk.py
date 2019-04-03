import typing as _typing


def hyphen_join(args: _typing.Tuple):
    return '-'.join((
        str(item)
        for item in args
    ))


def hyphen_split(val: str):
    return val.split('-')
