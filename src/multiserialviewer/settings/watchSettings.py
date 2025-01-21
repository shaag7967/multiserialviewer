from enum import Enum


class WatchSettings:
    class VariableType(Enum):
        number = 1
        word = 2

    def __init__(self, name: str, description: str, variableType: VariableType, pattern: str = ''):
        self.name: str = name
        self.description: str = description
        self.variableType: WatchSettings.VariableType = variableType
        self.pattern: str = pattern

