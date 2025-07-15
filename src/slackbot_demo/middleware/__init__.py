"""Middleware package for request processing."""

from .permission_middleware import PermissionMiddleware

__all__ = ["PermissionMiddleware"]
