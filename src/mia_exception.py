from enum import Enum

class MIASystem(Enum):
    DATABASE = 'DATABASE'
    API = 'API'

class MIASeverity(Enum):
    FATAL = 'FATAL'
    WARNING = 'WARNING'
    ALERT = 'ALERT'
    INFO = 'INFO'

class MIAException(BaseException):
    def __init__(self, system: MIASystem, severity: MIASeverity, message: str):
        super().__init__(f'{system.value} ERROR [{severity.value}]: {message}.')
