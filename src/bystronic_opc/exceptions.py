"""Exception classes for Bystronic OPC UA Client."""


class BystronicOPCError(Exception):
    """Base exception for Bystronic OPC operations."""
    pass


class ConnectionError(BystronicOPCError):
    """Raised when connection to OPC UA server fails."""
    pass


class DataError(BystronicOPCError):
    """Raised when data parsing or processing fails."""
    pass


class MethodCallError(BystronicOPCError):
    """Raised when OPC UA method call fails."""
    pass


class ConfigurationError(BystronicOPCError):
    """Raised when configuration is invalid."""
    pass