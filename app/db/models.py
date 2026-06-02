"""
Backward compatibility module.
Re-exports all models from app.models for legacy imports using app.db.models.
"""

import importlib
import sys

# Allow legacy imports such as ``app.db.models.users`` even though this file is
# a module rather than a directory package.
__path__ = []  # type: ignore[var-annotated]

# Re-export all models from app.models
from app.models.users import *
from app.models.projects import *
from app.models.tasks import *
from app.models.workspaces import *
from app.models.admin import *
from app.models.tags import *
from app.models.collaboration import *
from app.models.notifications import *
from app.models.analytics import *
from app.models.archive import *
from app.models.scheduling import *
from app.models.integration import *
from app.models.subscriptions import *
from app.models.personalization import *
from app.models.help_center import *
from app.models.onboarding import *
from app.models.reports import *
from app.models.integrations import *
from app.models.projects_extended import *


for _module_name in (
    "users",
    "projects",
    "tasks",
    "workspaces",
    "admin",
    "tags",
    "collaboration",
    "notifications",
    "analytics",
    "archive",
    "scheduling",
    "integration",
    "subscriptions",
    "personalization",
    "help_center",
    "onboarding",
    "reports",
    "integrations",
    "projects_extended",
):
    sys.modules[f"{__name__}.{_module_name}"] = importlib.import_module(
        f"app.models.{_module_name}"
    )
