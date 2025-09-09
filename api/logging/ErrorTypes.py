
class MarkDownConversionError(Exception):
    def __init__(self, reason, message="MarkDownConversionError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class NoTypeDeterminedError(Exception):
    def __init__(self, reason, message="NoTypeDeterminedError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'


class InlineNoTypeError(Exception):
    def __init__(self, reason, message="InlineNoTypeError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class EndAnswerNoTypeError(Exception):
    def __init__(self, reason, message="EndAnswerNoTypeError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class EMFImageError(Exception):
    def __init__(self, reason, message="EMFImageError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class MATEndStructureError(Exception):
    def __init__(self, reason, message="MATEndStructureError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class MATInlineStructureError(Exception):
    def __init__(self, reason, message="MATInlineStructureError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class MATNoMatchError(Exception):
    def __init__(self, reason, message="MATNoMatchError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class MATMissingChoiceError(Exception):
    def __init__(self, reason, message="MATMissingChoiceError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class MATMissingAnswerError(Exception):
    def __init__(self, reason, message="MATMissingAnswerError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class MATMissingOptionError(Exception):
    def __init__(self, reason, message="MATMissingOptionError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'
        
class FIBEndStructureError(Exception):
    def __init__(self, reason, message="FIBEndStructureError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class FIBInlineStructureError(Exception):
    def __init__(self, reason, message="FIBInlineStructureError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class TFEndStructureError(Exception):
    def __init__(self, reason, message="TFEndStructureError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class TFInlineStructureError(Exception):
    def __init__(self, reason, message="TFInlineStructureError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class TFNoAnswerError(Exception):
    def __init__(self, reason, message="TFNoAnswerError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class TFSelectedAnswerError(Exception):
    def __init__(self, reason, message="TFSelectedAnswerError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class MCEndStructureError(Exception):
    def __init__(self, reason, message="MCEndStructureError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class MCInlineStructureError(Exception):
    def __init__(self, reason, message="MCInlineStructureError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class ORDEndStructureError(Exception):
    def __init__(self, reason, message="ORDEndStructureError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class ORDInlineStructureError(Exception):
    def __init__(self, reason, message="ORDInlineStructureError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class MSEndStructureError(Exception):
    def __init__(self, reason, message="MSEndStructureError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class MSInlineStructureError(Exception):
    def __init__(self, reason, message="MSInlineStructureError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class WREndStructureError(Exception):
    def __init__(self, reason, message="WREndStructureError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'

class WRInlineStructureError(Exception):
    def __init__(self, reason, message="WRInlineStructureError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'
