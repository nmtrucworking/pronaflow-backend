"""
Scheduled background jobs for system maintenance.
"""
import asyncio
import logging

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.workspace import WorkspaceService

logger = logging.getLogger(__name__)


def _run_workspace_purge_once() -> None:
    db = SessionLocal()
    try:
        purged_count = WorkspaceService.purge_soft_deleted_workspaces(db)
        logger.info("Workspace purge completed. purged=%s", purged_count)
    except Exception:
        logger.exception("Workspace purge failed")
        db.rollback()
    finally:
        db.close()


async def run_workspace_purge_job(stop_event: asyncio.Event) -> None:
    """
    Periodically hard-delete soft-deleted workspaces past retention.
    """
    interval_seconds = max(settings.BACKGROUND_JOB_INTERVAL_HOURS, 1) * 3600
    while not stop_event.is_set():
        _run_workspace_purge_once()
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            continue
