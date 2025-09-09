class MCEndAnswerExistWarning(Exception):
    def __init__(self, reason, message="MCEndAnswerExistWarning"):
        self.reason = reason
        self.message = message

    def __str__(self):
        return f'{self.message} -> {self.reason}'


class MSEndAnswerExistWarning(Exception):
    def __init__(self, reason, message="MSEndAnswerExistWarning"):
        self.reason = reason
        self.message = message

    def __str__(self):
        return f'{self.message} -> {self.reason}'


class WREndAnswerExistWarning(Exception):
    def __init__(self, reason, message="WREndAnswerExistWarning"):
        self.reason = reason
        self.message = message

    def __str__(self):
        return f'{self.message} -> {self.reason}'


class RespondusTypeEWarning(Exception):
    def __init__(self, reason, message="RespondusTypeEWarning"):
        self.reason = reason
        self.message = message

    def __str__(self):
        return f'{self.message} -> {self.reason}'


class RespondusTypeMRWarning(Exception):
    def __init__(self, reason, message="RespondusTypeMRWarning"):
        self.reason = reason
        self.message = message

    def __str__(self):
        return f'{self.message} -> {self.reason}'


class RespondusTypeFMBWarning(Exception):
    def __init__(self, reason, message="RespondusTypeFMBWarning"):
        self.reason = reason
        self.message = message

    def __str__(self):
        return f'{self.message} -> {self.reason}'


class RespondusTypeMTWarning(Exception):
    def __init__(self, reason, message="RespondusTypeMTWarning"):
        self.reason = reason
        self.message = message

    def __str__(self):
        return f'{self.message} -> {self.reason}'
