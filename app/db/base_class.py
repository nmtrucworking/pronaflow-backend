"""
Summary-func: Cấu hình Declarative Base cho SQLAlchemy với quy tắc đặt tên chuẩn.
"""
import re
from typing import Any, Dict
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

# Namping Convention
# Reference: https://alembic.sqlalchemy.org/en/latest/naming.html
naming_convention = {
    "ix": "ix_%(column_0_label)s",                                          # Index
    "uq": "uq_%(table_name)s_%(column_0_name)s",                            # Unique Constraint
    "ck": "ck_%(table_name)s_%(constraint_name)s",                          # Check Constraint
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",    # Foreign Key
    "pk": "pk_%(table_name)s"                                               # Primary Key
}

class Base(DeclarativeBase):
    """
    Custom Declarative Base with naming conventions and table name generation.
    """
    metadata = MetaData(naming_convention=naming_convention)
    # Type annotation map
    type_annotation_map = {
        dict: JSONB,
        Dict[str, Any]: JSONB,
    }
    # Table Name Generation Rule
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Step 1: add underscore before capital letters (without first letter)
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__)
        # Step 2: convert to lowercase and add 's' for plural
        return name.lower() + 's'
