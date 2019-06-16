from outer_join.util.info import (
    ModelInfo as _ModelInfo,
)


class FieldDoesNotExist(Exception):
    def __init__(self, **kwargs):
        super().__init__(f"{self.__class__.__name__}: {kwargs}")


class JoinFieldError(Exception):
    def __init__(self, model: _ModelInfo, name: str):
        msg = f"Field {model.raw.__name__}.{name} does not exist in any base model"
        super().__init__(msg)
        self.model = model
        self.name = name


class MultiplePKDeclared(Exception):
    pass
