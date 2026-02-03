"""
Database initialization script for PronaFlow.
This script creates all database tables and runs initial setup.
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base
from app.core.config import settings


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    This uses SQLAlchemy's create_all() method based on the models.
    """
    print("=" * 60)
    print("PronaFlow Database Initialization")
    print("=" * 60)
    print(f"Database URL: {settings.DATABASE_URL}")
    print()
    
    try:
        # Test database connection
        print("Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✓ Connected to PostgreSQL: {version[:50]}...")
        print()
        
        # Create all tables
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully!")
        print()
        
        # List created tables
        print("Created tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
        print()
        
        print("=" * 60)
        print("Database initialization completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Run migrations: alembic revision --autogenerate -m 'Initial migration'")
        print("  2. Apply migrations: alembic upgrade head")
        print()
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        sys.exit(1)


def drop_all_tables() -> None:
    """
    Drop all tables from the database.
    USE WITH CAUTION - This will delete all data!
    """
    print("=" * 60)
    print("WARNING: Dropping all database tables!")
    print("=" * 60)
    
    confirmation = input("Type 'YES' to confirm: ")
    if confirmation != "YES":
        print("Operation cancelled.")
        return
    
    try:
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("✓ All tables dropped successfully!")
    except Exception as e:
        print(f"✗ Error dropping tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PronaFlow Database Management")
    parser.add_argument(
        "action",
        choices=["init", "drop"],
        help="Action to perform: 'init' to create tables, 'drop' to remove all tables"
    )
    
    args = parser.parse_args()
    
    if args.action == "init":
        init_db()
    elif args.action == "drop":
        drop_all_tables()
