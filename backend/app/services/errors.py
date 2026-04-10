class ServiceError(Exception):
    status_code = 400


class AuthorizationError(ServiceError):
    status_code = 403


class NotFoundError(ServiceError):
    status_code = 404


class ValidationError(ServiceError):
    status_code = 400
