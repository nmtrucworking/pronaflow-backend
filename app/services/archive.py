"""
Service layer for Module 8: Data Archiving and Compliance.

Implements business logic for archiving, trash bin management, data exports,
retention policies, and audit logging.

Ref: Module 8 - Data Archiving and Compliance
"""
import json
import zipfile
import io
from datetime import datetime, timedelta
from uuid import uuid4
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.archive import (
    ArchivePolicy, DeletedItem, ArchivedDataSnapshot, 
    DataExportRequest, DataRetentionLog, AuditLog
)
from app.models.projects import Project
from app.models.tasks import Task
from app.schemas.archive import (
    ArchivePolicyCreate, ArchivePolicyUpdate, DeletedItemRead,
    DataExportRequestCreate, DataExportRequestRead, AuditLogRead,
    AuditLogQueryFilter, BulkArchiveResponse
)


class ArchiveService:
    """
    Service for automated archiving strategy.
    Handles project archiving based on inactivity period.
    
    Ref: Module 8 - Feature 2.1 - Automated Archiving Strategy
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_archive_policy(self, workspace_id: str) -> Optional[ArchivePolicy]:
        """Get or create default archive policy for workspace."""
        policy = self.db.query(ArchivePolicy).filter(
            ArchivePolicy.workspace_id == workspace_id
        ).first()
        
        if not policy:
            # Create default policy
            policy = ArchivePolicy(
                id=str(uuid4()),
                workspace_id=workspace_id,
                inactive_days=180,
                is_enabled=True,
                trash_retention_days=30,
                auto_purge_enabled=True,
                export_link_expiry_hours=24,
                max_export_file_size_mb=500
            )
            self.db.add(policy)
            self.db.commit()
        
        return policy
    
    def update_archive_policy(
        self, 
        workspace_id: str, 
        policy_update: ArchivePolicyUpdate
    ) -> ArchivePolicy:
        """Update archive policy for workspace."""
        policy = self.get_archive_policy(workspace_id)
        
        update_data = policy_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(policy, field, value)
        
        policy.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(policy)
        return policy
    
    def should_archive_project(self, project: Project, inactive_days: int) -> bool:
        """
        Check if project should be archived.
        
        Ref: Module 8 - Feature 2.1 - AC 1 - Trigger Condition
        """
        if project.status not in ("DONE", "CANCELLED"):
            return False
        
        # Check if last activity is older than inactive_days
        if project.last_activity_at is None:
            project.last_activity_at = project.updated_at
        
        days_inactive = (datetime.utcnow() - project.last_activity_at).days
        return days_inactive >= inactive_days
    
    def archive_project(
        self, 
        project: Project, 
        archive_reason: Optional[str] = None,
        archived_by_user_id: Optional[str] = None
    ) -> ArchivedDataSnapshot:
        """
        Archive a project to cold storage.
        
        Ref: Module 8 - Feature 2.1 - AC 2 - State Transition & Immutability
        """
        # Get project snapshot data
        snapshot_data = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            "metadata": project.metadata or {}
        }
        
        # Count related items
        task_count = self.db.query(Task).filter(Task.project_id == project.id).count()
        
        # Create snapshot
        snapshot = ArchivedDataSnapshot(
            id=str(uuid4()),
            workspace_id=project.workspace_id,
            project_id=project.id,
            archived_at=datetime.utcnow(),
            archived_by_user_id=archived_by_user_id,
            project_data=snapshot_data,
            task_count=task_count,
            comment_count=0,  # TODO: count from comments table
            file_count=0,  # TODO: count from files table
            archive_reason=archive_reason
        )
        
        # Mark project as archived (set is_archived flag)
        if hasattr(project, 'is_archived'):
            project.is_archived = True
            project.status = "ARCHIVED"
            project.updated_at = datetime.utcnow()
        
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        
        return snapshot
    
    def run_auto_archive_job(self, workspace_id: str) -> BulkArchiveResponse:
        """
        Background job to automatically archive inactive projects.
        Called daily by scheduled task.
        """
        policy = self.get_archive_policy(workspace_id)
        
        if not policy.is_enabled:
            return BulkArchiveResponse(
                success=True,
                total_processed=0,
                archived_count=0,
                failed_count=0
            )
        
        # Find projects eligible for archiving
        projects_to_archive = self.db.query(Project).filter(
            and_(
                Project.workspace_id == workspace_id,
                Project.status.in_(["DONE", "CANCELLED"]),
                or_(
                    Project.last_activity_at < datetime.utcnow() - timedelta(days=policy.inactive_days),
                    Project.updated_at < datetime.utcnow() - timedelta(days=policy.inactive_days)
                )
            )
        ).all()
        
        archived_count = 0
        failed_count = 0
        errors = []
        
        for project in projects_to_archive:
            try:
                self.archive_project(
                    project, 
                    archive_reason="Auto-archived due to inactivity",
                    archived_by_user_id=None
                )
                archived_count += 1
            except Exception as e:
                failed_count += 1
                errors.append({"project_id": project.id, "error": str(e)})
        
        return BulkArchiveResponse(
            success=True,
            total_processed=len(projects_to_archive),
            archived_count=archived_count,
            failed_count=failed_count,
            errors=errors
        )


class TrashBinService:
    """
    Service for trash bin management with soft delete.
    
    Ref: Module 8 - Feature 2.2 - Trash Bin & Soft Delete
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def soft_delete(
        self,
        entity_type: str,
        entity_id: str,
        workspace_id: str,
        entity_data: Dict[str, Any],
        deleted_by_user_id: Optional[str] = None,
        deletion_reason: Optional[str] = None
    ) -> DeletedItem:
        """
        Soft delete an entity by marking it as deleted instead of physical deletion.
        
        Ref: Module 8 - Feature 2.2 - AC 1 - Soft Delete Mechanism
        """
        deleted_item = DeletedItem(
            id=str(uuid4()),
            workspace_id=workspace_id,
            entity_type=entity_type,
            entity_id=entity_id,
            deleted_by_user_id=deleted_by_user_id,
            deleted_at=datetime.utcnow(),
            original_data=entity_data,
            deletion_reason=deletion_reason,
            is_restored=False
        )
        
        self.db.add(deleted_item)
        self.db.commit()
        self.db.refresh(deleted_item)
        
        return deleted_item
    
    def restore_deleted_item(
        self,
        deleted_item_id: str,
        restored_by_user_id: Optional[str] = None
    ) -> DeletedItem:
        """
        Restore a deleted item from trash bin.
        
        Ref: Module 8 - Feature 2.2 - AC 3 - Restore Capability
        """
        deleted_item = self.db.query(DeletedItem).filter(
            DeletedItem.id == deleted_item_id
        ).first()
        
        if not deleted_item:
            raise ValueError(f"Deleted item {deleted_item_id} not found")
        
        # Mark as restored
        deleted_item.restored_at = datetime.utcnow()
        deleted_item.restored_by_user_id = restored_by_user_id
        deleted_item.is_restored = True
        deleted_item.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(deleted_item)
        
        return deleted_item
    
    def get_trash_bin(
        self,
        workspace_id: str,
        entity_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[DeletedItem], int]:
        """Get deleted items in trash bin."""
        query = self.db.query(DeletedItem).filter(
            and_(
                DeletedItem.workspace_id == workspace_id,
                DeletedItem.is_restored == False
            )
        )
        
        if entity_type:
            query = query.filter(DeletedItem.entity_type == entity_type)
        
        total = query.count()
        items = query.order_by(
            desc(DeletedItem.deleted_at)
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return items, total
    
    def run_auto_purge_job(self, workspace_id: str) -> int:
        """
        Background job to permanently delete items that exceeded retention period.
        
        Ref: Module 8 - Feature 2.2 - AC 2 - Auto-Purge Policy
        """
        policy = self.db.query(ArchivePolicy).filter(
            ArchivePolicy.workspace_id == workspace_id
        ).first()
        
        if not policy or not policy.auto_purge_enabled:
            return 0
        
        # Find items older than retention period
        cutoff_date = datetime.utcnow() - timedelta(days=policy.trash_retention_days)
        
        items_to_purge = self.db.query(DeletedItem).filter(
            and_(
                DeletedItem.workspace_id == workspace_id,
                DeletedItem.deleted_at < cutoff_date,
                DeletedItem.is_restored == False
            )
        ).all()
        
        # Hard delete (permanent removal)
        purged_count = 0
        for item in items_to_purge:
            self.db.delete(item)
            purged_count += 1
        
        self.db.commit()
        return purged_count


class DataExportService:
    """
    Service for asynchronous data export for GDPR compliance.
    
    Ref: Module 8 - Feature 2.3 - Data Export & Portability
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_export_request(
        self,
        workspace_id: str,
        requested_by_user_id: str,
        export_format: str = "json",
        scope: str = "all",
        scope_id: Optional[str] = None
    ) -> DataExportRequest:
        """
        Create an asynchronous export request.
        
        Ref: Module 8 - Feature 2.3 - AC 1 - Async Export Processing
        """
        export_request = DataExportRequest(
            id=str(uuid4()),
            workspace_id=workspace_id,
            requested_by_user_id=requested_by_user_id,
            export_format=export_format,
            scope=scope,
            scope_id=scope_id,
            status="pending",
            progress_percent=0,
            download_token=self._generate_download_token(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        self.db.add(export_request)
        self.db.commit()
        self.db.refresh(export_request)
        
        return export_request
    
    def _generate_download_token(self) -> str:
        """Generate secure download token."""
        import hashlib
        import secrets
        random_bytes = secrets.token_bytes(32)
        return hashlib.sha256(random_bytes).hexdigest()
    
    def generate_json_export(self, export_request: DataExportRequest) -> bytes:
        """
        Generate JSON export file.
        
        Ref: Module 8 - Feature 2.3 - AC 2 - Data Structure Standard
        """
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "workspace_id": export_request.workspace_id,
            "scope": export_request.scope,
            "projects": [],
            "tasks": [],
            "comments": []
        }
        
        # Fetch data based on scope
        if export_request.scope == "all" or export_request.scope == "workspace":
            projects = self.db.query(Project).filter(
                Project.workspace_id == export_request.workspace_id
            ).all()
        elif export_request.scope == "projects" and export_request.scope_id:
            projects = self.db.query(Project).filter(
                Project.id == export_request.scope_id
            ).all()
        else:
            projects = []
        
        # Serialize projects
        for project in projects:
            export_data["projects"].append({
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "created_at": project.created_at.isoformat() if project.created_at else None
            })
        
        # TODO: Fetch and serialize tasks and comments
        
        return json.dumps(export_data, indent=2).encode('utf-8')
    
    def update_export_status(
        self,
        export_id: str,
        status: str,
        progress_percent: int = 0,
        error_message: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> DataExportRequest:
        """Update export request status."""
        export_request = self.db.query(DataExportRequest).filter(
            DataExportRequest.id == export_id
        ).first()
        
        if not export_request:
            raise ValueError(f"Export request {export_id} not found")
        
        export_request.status = status
        export_request.progress_percent = progress_percent
        export_request.error_message = error_message
        
        if file_path:
            export_request.file_path = file_path
        
        if status == "completed":
            export_request.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(export_request)
        
        return export_request
    
    def increment_download_count(self, export_id: str) -> None:
        """Increment download counter for tracking."""
        export_request = self.db.query(DataExportRequest).filter(
            DataExportRequest.id == export_id
        ).first()
        
        if export_request:
            export_request.download_count += 1
            self.db.commit()


class RetentionService:
    """
    Service for data retention policy enforcement.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_retention_action(
        self,
        workspace_id: str,
        action_type: str,
        data_retention_type: str,
        entity_type: str,
        entity_id: str,
        rows_affected: int = 0,
        executed_by_user_id: Optional[str] = None
    ) -> DataRetentionLog:
        """Log a retention policy action."""
        log_entry = DataRetentionLog(
            id=str(uuid4()),
            workspace_id=workspace_id,
            action_type=action_type,
            data_retention_type=data_retention_type,
            entity_type=entity_type,
            entity_id=entity_id,
            executed_at=datetime.utcnow(),
            executed_by_user_id=executed_by_user_id,
            rows_affected=rows_affected
        )
        
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        
        return log_entry


class AuditService:
    """
    Service for comprehensive audit logging.
    
    Ref: Module 8 - Section 3.2 - Data Retention Policy (90-day retention)
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(
        self,
        workspace_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        status_code: str = "success",
        error_message: Optional[str] = None
    ) -> AuditLog:
        """
        Log a system action for audit trail.
        """
        audit_log = AuditLog(
            id=str(uuid4()),
            workspace_id=workspace_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            changes=changes,
            status_code=status_code,
            error_message=error_message,
            logged_at=datetime.utcnow()
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    def get_audit_logs(
        self,
        workspace_id: str,
        filters: Optional[AuditLogQueryFilter] = None
    ) -> tuple[List[AuditLog], int]:
        """Query audit logs with filters."""
        if filters is None:
            filters = AuditLogQueryFilter()
        
        query = self.db.query(AuditLog).filter(
            AuditLog.workspace_id == workspace_id
        )
        
        if filters.action:
            query = query.filter(AuditLog.action == filters.action)
        if filters.resource_type:
            query = query.filter(AuditLog.resource_type == filters.resource_type)
        if filters.user_id:
            query = query.filter(AuditLog.user_id == filters.user_id)
        if filters.status_code:
            query = query.filter(AuditLog.status_code == filters.status_code)
        if filters.from_date:
            query = query.filter(AuditLog.logged_at >= filters.from_date)
        if filters.to_date:
            query = query.filter(AuditLog.logged_at <= filters.to_date)
        
        total = query.count()
        logs = query.order_by(
            desc(AuditLog.logged_at)
        ).offset((filters.page - 1) * filters.page_size).limit(
            filters.page_size
        ).all()
        
        return logs, total
