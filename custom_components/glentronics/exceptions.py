"""Exceptions."""

class ApiException(Exception):
    """General API exception."""


class AuthenticationError(ApiException):
    """To indicate there is an issue authenticating."""
