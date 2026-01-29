"""FastAPI dependencies."""

from app.interfaces.http.dependencies.identity import (
    get_create_tenant_use_case,
    get_create_user_use_case,
)

__all__ = ["get_create_tenant_use_case", "get_create_user_use_case"]
