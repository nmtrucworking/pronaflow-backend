"""
Repository layer for Workspace operations.
Handles database queries for Workspace, WorkspaceMember, and related entities.
Ref: Module 2 - Multi-tenancy Workspace Governance
"""
import uuid
from typing import List, Optional, Tuple
from datetime import datetime, timedelta

from sqlalchemy import select, and_, or_, func, delete
from sqlalchemy.orm import Session, joinedload

from app.db.models.workspaces import (
    Workspace,
    WorkspaceMember,
    WorkspaceInvitation,
    WorkspaceAccessLog,
    WorkspaceSetting,
)
from app.db.models.users import User
from app.db.enums import WorkspaceRole


class WorkspaceRepository:
    """Repository for Workspace operations"""

    def __init__(self, db: Session):
        self.db = db

    # ===== Workspace CRUD =====

    def create(self, workspace: Workspace) -> Workspace:
        """Create a new workspace"""
        self.db.add(workspace)
        self.db.flush()
        return workspace

    def get_by_id(self, workspace_id: uuid.UUID, include_deleted: bool = False) -> Optional[Workspace]:
        """Get workspace by ID"""
        query = select(Workspace).where(Workspace.id == workspace_id)
        
        if not include_deleted:
            query = query.where(Workspace.is_deleted == False)
            
        return self.db.scalar(query)

    def get_by_id_with_relations(self, workspace_id: uuid.UUID) -> Optional[Workspace]:
        """Get workspace with all relations loaded"""
        query = (
            select(Workspace)
            .options(
                joinedload(Workspace.members),
                joinedload(Workspace.settings),
                joinedload(Workspace.owner)
            )
            .where(
                and_(
                    Workspace.id == workspace_id,
                    Workspace.is_deleted == False
                )
            )
        )
        return self.db.scalar(query)

    def list_by_user(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 10,
        include_inactive: bool = False
    ) -> Tuple[List[Workspace], int]:
        """List workspaces where user is a member"""
        filters = [
            WorkspaceMember.user_id == user_id,
            Workspace.is_deleted == False,
        ]
        
        if not include_inactive:
            filters.append(WorkspaceMember.is_active == True)

        query = (
            select(Workspace)
            .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
            .where(and_(*filters))
            .offset(skip)
            .limit(limit)
        )

        count_query = (
            select(func.count(Workspace.id))
            .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
            .where(and_(*filters))
        )

        workspaces = self.db.scalars(query).unique().all()
        total = self.db.scalar(count_query)

        return workspaces, total

    def update(self, workspace: Workspace) -> Workspace:
        """Update workspace"""
        self.db.flush()
        return workspace

    def soft_delete(self, workspace: Workspace) -> bool:
        """Soft delete workspace"""
        workspace.soft_delete()
        self.db.flush()
        return True

    def hard_delete(self, workspace_id: uuid.UUID) -> bool:
        """Permanently delete workspace"""
        result = self.db.execute(
            delete(Workspace).where(Workspace.id == workspace_id)
        )
        return result.rowcount > 0

    def restore(self, workspace: Workspace) -> Workspace:
        """Restore soft-deleted workspace"""
        workspace.restore()
        self.db.flush()
        return workspace

    # ===== Admin operations =====

    def list_deleted(
        self,
        skip: int = 0,
        limit: int = 50,
        older_than_days: Optional[int] = None
    ) -> Tuple[List[Workspace], int]:
        """List soft-deleted workspaces for admin"""
        filters = [Workspace.is_deleted == True]
        
        if older_than_days:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            filters.append(Workspace.deleted_at <= cutoff_date)

        query = (
            select(Workspace)
            .where(and_(*filters))
            .offset(skip)
            .limit(limit)
        )

        count_query = select(func.count(Workspace.id)).where(and_(*filters))

        workspaces = self.db.scalars(query).all()
        total = self.db.scalar(count_query)

        return workspaces, total


class WorkspaceMemberRepository:
    """Repository for WorkspaceMember operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, member: WorkspaceMember) -> WorkspaceMember:
        """Add a member to workspace"""
        self.db.add(member)
        self.db.flush()
        return member

    def get_by_workspace_and_user(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[WorkspaceMember]:
        """Get member by workspace and user"""
        query = select(WorkspaceMember).where(
            and_(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id
            )
        )
        return self.db.scalar(query)

    def list_by_workspace(
        self,
        workspace_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        active_only: bool = True
    ) -> Tuple[List[WorkspaceMember], int]:
        """List members of a workspace"""
        filters = [WorkspaceMember.workspace_id == workspace_id]
        
        if active_only:
            filters.append(WorkspaceMember.is_active == True)

        query = (
            select(WorkspaceMember)
            .where(and_(*filters))
            .offset(skip)
            .limit(limit)
        )

        count_query = select(func.count(WorkspaceMember.id)).where(and_(*filters))

        members = self.db.scalars(query).all()
        total = self.db.scalar(count_query)

        return members, total

    def update(self, member: WorkspaceMember) -> WorkspaceMember:
        """Update member"""
        self.db.flush()
        return member

    def deactivate(self, member: WorkspaceMember) -> WorkspaceMember:
        """Deactivate member (soft removal)"""
        member.is_active = False
        member.left_at = datetime.utcnow()
        self.db.flush()
        return member

    def delete(self, member: WorkspaceMember) -> bool:
        """Delete member"""
        self.db.delete(member)
        self.db.flush()
        return True


class WorkspaceInvitationRepository:
    """Repository for WorkspaceInvitation operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, invitation: WorkspaceInvitation) -> WorkspaceInvitation:
        """Create invitation"""
        self.db.add(invitation)
        self.db.flush()
        return invitation

    def get_by_id(self, invitation_id: uuid.UUID) -> Optional[WorkspaceInvitation]:
        """Get invitation by ID"""
        query = select(WorkspaceInvitation).where(WorkspaceInvitation.id == invitation_id)
        return self.db.scalar(query)

    def get_by_token(self, token_hash: str) -> Optional[WorkspaceInvitation]:
        """Get invitation by token hash"""
        query = select(WorkspaceInvitation).where(
            and_(
                WorkspaceInvitation.token_hash == token_hash,
                WorkspaceInvitation.accepted_at.is_(None),
                WorkspaceInvitation.expires_at > datetime.utcnow()
            )
        )
        return self.db.scalar(query)

    def list_pending_by_workspace(
        self,
        workspace_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[WorkspaceInvitation], int]:
        """List pending invitations for workspace"""
        filters = [
            WorkspaceInvitation.workspace_id == workspace_id,
            WorkspaceInvitation.accepted_at.is_(None),
            WorkspaceInvitation.expires_at > datetime.utcnow()
        ]

        query = (
            select(WorkspaceInvitation)
            .where(and_(*filters))
            .offset(skip)
            .limit(limit)
        )

        count_query = select(func.count(WorkspaceInvitation.id)).where(and_(*filters))

        invitations = self.db.scalars(query).all()
        total = self.db.scalar(count_query)

        return invitations, total

    def update(self, invitation: WorkspaceInvitation) -> WorkspaceInvitation:
        """Update invitation"""
        self.db.flush()
        return invitation

    def delete(self, invitation: WorkspaceInvitation) -> bool:
        """Delete invitation"""
        self.db.delete(invitation)
        self.db.flush()
        return True


class WorkspaceAccessLogRepository:
    """Repository for WorkspaceAccessLog operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, access_log: WorkspaceAccessLog) -> WorkspaceAccessLog:
        """Create access log"""
        self.db.add(access_log)
        self.db.flush()
        return access_log

    def get_last_accessed(self, user_id: uuid.UUID) -> Optional[WorkspaceAccessLog]:
        """Get user's last accessed workspace"""
        query = (
            select(WorkspaceAccessLog)
            .where(WorkspaceAccessLog.user_id == user_id)
            .order_by(WorkspaceAccessLog.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(query)

    def list_by_workspace(
        self,
        workspace_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[WorkspaceAccessLog], int]:
        """List access logs for workspace"""
        filters = [WorkspaceAccessLog.workspace_id == workspace_id]
        
        if user_id:
            filters.append(WorkspaceAccessLog.user_id == user_id)

        query = (
            select(WorkspaceAccessLog)
            .where(and_(*filters))
            .order_by(WorkspaceAccessLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        count_query = select(func.count(WorkspaceAccessLog.id)).where(and_(*filters))

        logs = self.db.scalars(query).all()
        total = self.db.scalar(count_query)

        return logs, total


class WorkspaceSettingRepository:
    """Repository for WorkspaceSetting operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, setting: WorkspaceSetting) -> WorkspaceSetting:
        """Create workspace setting"""
        self.db.add(setting)
        self.db.flush()
        return setting

    def get_by_workspace(self, workspace_id: uuid.UUID) -> Optional[WorkspaceSetting]:
        """Get settings for workspace"""
        query = select(WorkspaceSetting).where(WorkspaceSetting.workspace_id == workspace_id)
        return self.db.scalar(query)

    def update(self, setting: WorkspaceSetting) -> WorkspaceSetting:
        """Update workspace setting"""
        self.db.flush()
        return setting
