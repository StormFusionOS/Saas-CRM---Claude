"""
Minimal Pydantic stub for offline testing.

PRODUCTION NOTE: Replace this stub with the real Pydantic package:
    pip install pydantic[email]

This stub provides basic BaseModel functionality for schema validation.
"""

from typing import Any, ClassVar, Dict, Optional, Type, TypeVar, get_type_hints
from dataclasses import dataclass, field, fields, MISSING
from enum import Enum


T = TypeVar('T', bound='BaseModel')


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(self, errors: list):
        self.errors = errors
        super().__init__(str(errors))


class ConfigDict:
    """Configuration for Pydantic models."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@dataclass
class Field:
    """Field configuration for model attributes."""

    default: Any = MISSING
    default_factory: Any = MISSING
    alias: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    gt: Optional[float] = None
    ge: Optional[float] = None
    lt: Optional[float] = None
    le: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None


def Field(
    default=...,
    *,
    default_factory=None,
    alias=None,
    title=None,
    description=None,
    gt=None,
    ge=None,
    lt=None,
    le=None,
    min_length=None,
    max_length=None,
    pattern=None,
    **kwargs
):
    """Create a field with validation rules."""
    if default is not ... and default_factory is not None:
        raise ValueError("Cannot specify both default and default_factory")

    if default_factory is not None:
        return field(default_factory=default_factory)
    elif default is not ...:
        return field(default=default)
    else:
        return field()


class BaseModel:
    """
    Minimal BaseModel implementation for testing.

    Provides basic field validation and serialization without
    the full complexity of Pydantic.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict()

    def __init__(self, **data):
        # Get type hints for validation
        hints = get_type_hints(self.__class__)

        # Set attributes from data
        for key, value in data.items():
            if hasattr(self.__class__, key) or key in hints:
                setattr(self, key, value)

        # Set defaults for missing fields
        for key, hint in hints.items():
            if not hasattr(self, key):
                default = getattr(self.__class__, key, None)
                if default is not None:
                    setattr(self, key, default)

    def dict(self, **kwargs) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = {}
        hints = get_type_hints(self.__class__)

        for key in hints.keys():
            if hasattr(self, key):
                value = getattr(self, key)
                if isinstance(value, BaseModel):
                    result[key] = value.dict()
                elif isinstance(value, list):
                    result[key] = [
                        item.dict() if isinstance(item, BaseModel) else item
                        for item in value
                    ]
                else:
                    result[key] = value

        return result

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Alias for dict() - Pydantic v2 style."""
        return self.dict(**kwargs)

    @classmethod
    def model_validate(cls: Type[T], obj: Any) -> T:
        """Validate and create model from object."""
        if isinstance(obj, dict):
            return cls(**obj)
        elif isinstance(obj, cls):
            return obj
        else:
            raise ValidationError([{"msg": "Invalid input type"}])

    @classmethod
    def parse_obj(cls: Type[T], obj: Any) -> T:
        """Alias for model_validate() - Pydantic v1 style."""
        return cls.model_validate(obj)

    class Config:
        """Model configuration."""

        arbitrary_types_allowed = True
        from_attributes = True
        populate_by_name = True


class EmailStr(str):
    """Email string type."""

    pass


class HttpUrl(str):
    """HTTP URL string type."""

    pass


class SecretStr:
    """Secret string that hides its value."""

    def __init__(self, value: str):
        self._value = value

    def get_secret_value(self) -> str:
        """Get the secret value."""
        return self._value

    def __str__(self):
        return "**********"

    def __repr__(self):
        return "SecretStr('**********')"


__all__ = [
    "BaseModel",
    "Field",
    "ValidationError",
    "ConfigDict",
    "EmailStr",
    "HttpUrl",
    "SecretStr",
]
