"""
Script to check database completeness against docs
"""
import os
import re
from pathlib import Path

# Get all entities from docs
docs_path = Path(r"e:\Workspace\project\pronaflow\backend\docs\docs - PronaFlow React&FastAPI\02-Architeture\Entities")
entities_from_docs = set()

for md_file in docs_path.glob("*.md"):
    # Get entity name from filename
    entity_name = md_file.stem
    if entity_name != "files":  # Skip the index file
        entities_from_docs.add(entity_name)

print(f"Total entities in docs: {len(entities_from_docs)}")

# Get all models from current implementation
from app.db.declarative_base import Base
from app.db import models

# Get model class names
models_implemented = set()
for table_name in Base.metadata.tables.keys():
    # Convert table name to potential model names
    # e.g., "users" -> "User", "workspace_members" -> "WorkspaceMember"
    parts = table_name.split('_')
    model_name = ''.join([p.capitalize() for p in parts])
    models_implemented.add(model_name)

print(f"Total models implemented: {len(models_implemented)}")
print()

# Find missing entities
missing = entities_from_docs - models_implemented
if missing:
    print(f"MISSING ENTITIES ({len(missing)}):")
    for entity in sorted(missing):
        print(f"  - {entity}")
else:
    print("✓ All entities from docs are implemented!")

# Find extra models
extra = models_implemented - entities_from_docs
if extra:
    print()
    print(f"EXTRA MODELS NOT IN DOCS ({len(extra)}):")
    for model in sorted(extra):
        print(f"  - {model}")
