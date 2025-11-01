"""
CRM API SQLAlchemy Models.

These models are used for Alembic migrations and schema diff tooling.
For in-memory operations in tests, see models.py

PRODUCTION NOTE: Install SQLAlchemy for real database operations:
    pip install sqlalchemy psycopg2-binary alembic
"""

from datetime import datetime
from typing import List

# Minimal SQLAlchemy stubs for schema definition
# In production, import from sqlalchemy


class Column:
    """Stub for SQLAlchemy Column."""

    def __init__(self, *args, **kwargs):
        self.type = args[0] if args else None
        self.primary_key = kwargs.get('primary_key', False)
        self.nullable = kwargs.get('nullable', True)
        self.unique = kwargs.get('unique', False)
        self.index = kwargs.get('index', False)
        self.default = kwargs.get('default')
        self.server_default = kwargs.get('server_default')


class Integer:
    """Stub for Integer type."""
    pass


class String:
    """Stub for String type."""

    def __init__(self, length=None):
        self.length = length


class Text:
    """Stub for Text type."""
    pass


class Float:
    """Stub for Float type."""
    pass


class Boolean:
    """Stub for Boolean type."""
    pass


class DateTime:
    """Stub for DateTime type."""
    pass


class JSON:
    """Stub for JSON type."""
    pass


class ARRAY:
    """Stub for ARRAY type."""

    def __init__(self, item_type):
        self.item_type = item_type


class ForeignKey:
    """Stub for ForeignKey."""

    def __init__(self, column, **kwargs):
        self.column = column


class relationship:
    """Stub for relationship."""

    def __init__(self, target, **kwargs):
        self.target = target
        self.back_populates = kwargs.get('back_populates')


class declarative_base:
    """Stub for declarative base."""

    def __init__(self):
        pass

    def __call__(self):
        return Base


class Base:
    """Base model class."""

    __tablename__ = None
    metadata = None


# Define models for schema tooling


class UserModel(Base):
    """SQLAlchemy User model for migrations."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    roles = Column(ARRAY(String(50)), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class ContactModel(Base):
    """SQLAlchemy Contact model for migrations."""

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(50), index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    company = Column(String(255))
    title = Column(String(100))
    tags = Column(ARRAY(String(50)))
    custom_fields = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    last_contacted_at = Column(DateTime)


class LeadModel(Base):
    """SQLAlchemy Lead model for migrations."""

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    status = Column(String(50), default="NEW", index=True)
    source = Column(String(50), default="MANUAL")
    value = Column(Float)
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    probability = Column(Integer, default=0)
    expected_close_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    won_at = Column(DateTime)
    lost_at = Column(DateTime)


class InteractionModel(Base):
    """SQLAlchemy Interaction model for migrations."""

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    interaction_type = Column(String(50), default="NOTE")
    direction = Column(String(20), default="INBOUND")
    subject = Column(String(500))
    body = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class AutoReplyRuleModel(Base):
    """SQLAlchemy AutoReplyRule model for migrations."""

    __tablename__ = "auto_reply_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    trigger_source = Column(String(50), nullable=False)
    trigger_conditions = Column(JSON)
    reply_template = Column(Text, nullable=False)
    reply_channel = Column(String(50), default="EMAIL")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# Export models for Alembic
__all__ = [
    "Base",
    "UserModel",
    "ContactModel",
    "LeadModel",
    "InteractionModel",
    "AutoReplyRuleModel",
]
