class BaseIBANException(ValueError):
    pass


class InvalidLength(BaseIBANException):
    pass


class InvalidStructure(BaseIBANException):
    pass


class InvalidChecksumDigits(BaseIBANException):
    pass


class InvalidCountryCode(BaseIBANException):
    pass
