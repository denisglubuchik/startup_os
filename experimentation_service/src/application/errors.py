class ApplicationError(Exception):
    """Base error for application-layer failures."""


class NotFoundError(ApplicationError):
    pass


class ValidationError(ApplicationError):
    pass
