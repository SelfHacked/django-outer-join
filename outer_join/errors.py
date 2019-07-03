from model_wrappers import (
    ModelWrapper as _ModelInfo,
)


class JoinFieldError(Exception):
    def __init__(self, model: _ModelInfo, name: str):
        msg = f"Field {model.raw.__name__}.{name} does not exist in any base model"
        super().__init__(msg)
        self.model = model
        self.name = name


class MultiplePKDeclared(Exception):
    pass
