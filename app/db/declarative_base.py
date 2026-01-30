"""
SQLAlchemy Declarative Base Configuration.
Provides the base class for all ORM models with naming conventions and type mappings.
"""
import re
from typing import Any, Dict
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB


# Naming Convention for constraints and indexes
# Reference: https://alembic.sqlalchemy.org/en/latest/naming.html
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


class Base(DeclarativeBase):
    """
    Custom Declarative Base class for all ORM models.
    
    Features:
    - Automatic table name generation (snake_case with 's' suffix)
    - Type annotation mapping (dict → JSONB)
    - Naming conventions for constraints and indexes
    """
    metadata = MetaData(naming_convention=naming_convention)
    
    # Type annotation map for PostgreSQL-specific types
    type_annotation_map = {
        dict: JSONB,
        Dict[str, Any]: JSONB,
    }
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Automatically generate table names from class names.
        Converts ClassName → class_names (snake_case with plural suffix)
        
        Examples:
            User → users
            WorkspaceMember → workspace_members
        """
        # Insert underscore before capital letters (except the first letter)
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__)
        # Convert to lowercase and add 's' for plural
        return name.lower() + 's'
