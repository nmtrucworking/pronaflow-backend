"""
Service layer for Workspace management.
Handles business logic for workspace CRUD operations, member management, and invitations.
Ref: docs/docs - PronaFlow React&FastAPI/01-Requirements/Functional-Modules/2 - Multi-tenancy Workspace Governance.md
"""
import uuid
import secrets
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.db.models.workspaces import (
    Workspace,
    WorkspaceMember,
    WorkspaceInvitation,
    WorkspaceAccessLog,
    WorkspaceSetting,
)
from app.db.models.users import User
from app.db.enums import WorkspaceRole
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceMemberCreate,
    WorkspaceMemberUpdate,
    WorkspaceInvitationCreate,
    WorkspaceSettingCreate,
    WorkspaceSettingUpdate,
)
from app.services.workspace_validation import WorkspaceValidator


class WorkspaceService:
    """Service for workspace management"""

    @staticmethod
    def create_workspace(
        db: Session,
        workspace_data: WorkspaceCreate,
        owner_id: uuid.UUID,
    ) -> Workspace:
        """
        Create a new workspace.
        
        Args:
            db: Database session
            workspace_data: Workspace creation data
            owner_id: UUID of workspace owner (current user)
            
        Returns:
            Created workspace object
            
        Ref: AC 1 - Khởi tạo thành công
        """
        # Validate workspace name (Module 2 - AC 3: Validation)
        is_valid, error = WorkspaceValidator.validate_workspace_name(workspace_data.name)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Validate description if provided
        if workspace_data.description:
            is_valid, error = WorkspaceValidator.validate_description(workspace_data.description)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
        
        workspace = Workspace(
            name=workspace_data.name,
            description=workspace_data.description,
            owner_id=owner_id,
            status="ACTIVE",
        )

        db.add(workspace)
        db.flush()  # Flush to get the workspace ID

        # Automatically add owner as member with OWNER role
        owner_member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=owner_id,
            role=WorkspaceRole.OWNER,
            is_active=True,
        )
        db.add(owner_member)

        # Create default settings
        default_settings = WorkspaceSetting(
            workspace_id=workspace.id,
            timezone="UTC",
            work_days="Mon,Tue,Wed,Thu,Fri",
            work_hours='{"start": "09:00", "end": "18:00"}',
        )
        db.add(default_settings)

        db.commit()
        db.refresh(workspace)
        return workspace

    @staticmethod
    def get_workspace(db: Session, workspace_id: uuid.UUID) -> Optional[Workspace]:
        """
        Get a workspace by ID.
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            
        Returns:
            Workspace object or None if not found
        """
        stmt = select(Workspace).where(
            and_(
                Workspace.id == workspace_id,
                Workspace.is_deleted == False,
            )
        )
        return db.scalar(stmt)

    @staticmethod
    def list_user_workspaces(
        db: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[Workspace], int]:
        """
        List all active workspaces for a user.
        
        Args:
            db: Database session
            user_id: User UUID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            Tuple of (workspaces list, total count)
        """
        # Get workspaces where user is a member or owner
        stmt = (
            select(Workspace)
            .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
            .where(
                and_(
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.is_active == True,
                    Workspace.is_deleted == False,
                )
            )
            .offset(skip)
            .limit(limit)
        )

        count_stmt = (
            select(func.count(Workspace.id))
            .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
            .where(
                and_(
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.is_active == True,
                    Workspace.is_deleted == False,
                )
            )
        )

        workspaces = db.scalars(stmt).unique().all()
        total = db.scalar(count_stmt)

        return workspaces, total

    @staticmethod
    def update_workspace(
        db: Session,
        workspace_id: uuid.UUID,
        update_data: WorkspaceUpdate,
    ) -> Optional[Workspace]:
        """
        Update workspace information.
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            update_data: Update data
            
        Returns:
            Updated workspace or None if not found
        """
        workspace = WorkspaceService.get_workspace(db, workspace_id)
        if not workspace:
            return None

        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(workspace, key):
                setattr(workspace, key, value)

        db.commit()
        db.refresh(workspace)
        return workspace

    @staticmethod
    def delete_workspace(db: Session, workspace_id: uuid.UUID) -> bool:
        """
        Soft delete a workspace.
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            
        Returns:
            True if deleted, False if not found
        """
        workspace = WorkspaceService.get_workspace(db, workspace_id)
        if not workspace:
            return False

        workspace.soft_delete()
        db.commit()
        return True


class WorkspaceMemberService:
    """Service for workspace member management"""

    @staticmethod
    def add_member(
        db: Session,
        workspace_id: uuid.UUID,
        member_data: WorkspaceMemberCreate,
    ) -> Optional[WorkspaceMember]:
        """
        Add a member to workspace.
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            member_data: Member creation data
            
        Returns:
            Created WorkspaceMember or None if user not found
        """
        # Check if user exists
        user = db.scalar(select(User).where(User.id == member_data.user_id))
        if not user:
            return None

        # Check if already member
        existing = db.scalar(
            select(WorkspaceMember).where(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == member_data.user_id,
                )
            )
        )
        if existing:
            # Reactivate if was inactive
            if not existing.is_active:
                existing.is_active = True
                existing.left_at = None
                db.commit()
            return existing

        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=member_data.user_id,
            role=member_data.role,
            is_active=True,
        )

        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def get_member(
        db: Session,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[WorkspaceMember]:
        """
        Get a workspace member.
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            user_id: User UUID
            
        Returns:
            WorkspaceMember or None
        """
        stmt = select(WorkspaceMember).where(
            and_(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        return db.scalar(stmt)

    @staticmethod
    def list_members(
        db: Session,
        workspace_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[WorkspaceMember], int]:
        """
        List workspace members.
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            Tuple of (members list, total count)
        """
        count_stmt = select(func.count(WorkspaceMember.id)).where(
            WorkspaceMember.workspace_id == workspace_id
        )

        stmt = (
            select(WorkspaceMember)
            .where(WorkspaceMember.workspace_id == workspace_id)
            .offset(skip)
            .limit(limit)
        )

        members = db.scalars(stmt).all()
        total = db.scalar(count_stmt)

        return members, total

    @staticmethod
    def update_member(
        db: Session,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        update_data: WorkspaceMemberUpdate,
    ) -> Optional[WorkspaceMember]:
        """
        Update member role or status.
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            user_id: User UUID
            update_data: Update data
            
        Returns:
            Updated WorkspaceMember or None
        """
        member = WorkspaceMemberService.get_member(db, workspace_id, user_id)
        if not member:
            return None

        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(member, key):
                setattr(member, key, value)

        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def remove_member(
        db: Session,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """
        Remove a member from workspace (soft removal).
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            user_id: User UUID
            
        Returns:
            True if removed, False if not found
        """
        member = WorkspaceMemberService.get_member(db, workspace_id, user_id)
        if not member:
            return False

        member.is_active = False
        member.left_at = datetime.utcnow()
        db.commit()
        return True


class WorkspaceInvitationService:
    """Service for workspace invitation management"""

    @staticmethod
    def create_invitation(
        db: Session,
        workspace_id: uuid.UUID,
        invited_by: uuid.UUID,
        invitation_data: WorkspaceInvitationCreate,
        expires_in_hours: int = 48,
    ) -> WorkspaceInvitation:
        """
        Create a workspace invitation.
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            invited_by: User ID of inviter
            invitation_data: Invitation data
            expires_in_hours: Hours until expiration (default 48h)
            
        Returns:
            Created WorkspaceInvitation
            
        Ref: AC 2 - Member Invitation & Management
        """
        # Generate secure token
        token = secrets.token_urlsafe(32)
        token_hash = hash(token)  # In production, use proper hash function

        invitation = WorkspaceInvitation(
            workspace_id=workspace_id,
            email=invitation_data.email,
            invited_by=invited_by,
            invited_role=invitation_data.invited_role,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours),
        )

        db.add(invitation)
        db.commit()
        db.refresh(invitation)

        return invitation

    @staticmethod
    def get_invitation(
        db: Session,
        invitation_id: uuid.UUID,
    ) -> Optional[WorkspaceInvitation]:
        """
        Get an invitation by ID.
        
        Args:
            db: Database session
            invitation_id: Invitation UUID
            
        Returns:
            WorkspaceInvitation or None
        """
        stmt = select(WorkspaceInvitation).where(WorkspaceInvitation.id == invitation_id)
        return db.scalar(stmt)

    @staticmethod
    def list_pending_invitations(
        db: Session,
        workspace_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[WorkspaceInvitation], int]:
        """
        List pending invitations for a workspace.
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            skip: Number to skip
            limit: Max records
            
        Returns:
            Tuple of (invitations list, total count)
        """
        count_stmt = (
            select(func.count(WorkspaceInvitation.id))
            .where(
                and_(
                    WorkspaceInvitation.workspace_id == workspace_id,
                    WorkspaceInvitation.accepted_at.is_(None),
                    WorkspaceInvitation.expires_at > datetime.utcnow(),
                )
            )
        )

        stmt = (
            select(WorkspaceInvitation)
            .where(
                and_(
                    WorkspaceInvitation.workspace_id == workspace_id,
                    WorkspaceInvitation.accepted_at.is_(None),
                    WorkspaceInvitation.expires_at > datetime.utcnow(),
                )
            )
            .offset(skip)
            .limit(limit)
        )

        invitations = db.scalars(stmt).all()
        total = db.scalar(count_stmt)

        return invitations, total

    @staticmethod
    def accept_invitation(
        db: Session,
        invitation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[WorkspaceMember]:
        """
        Accept a workspace invitation and add user as member.
        
        Args:
            db: Database session
            invitation_id: Invitation UUID
            user_id: User UUID accepting invitation
            
        Returns:
            Created WorkspaceMember or None if invitation invalid/expired
        """
        invitation = WorkspaceInvitationService.get_invitation(db, invitation_id)

        # Validate invitation
        if not invitation:
            return None
        if invitation.accepted_at is not None:
            return None  # Already accepted
        if invitation.expires_at < datetime.utcnow():
            return None  # Expired

        # Add as member with invitation role
        member_data = WorkspaceMemberCreate(
            user_id=user_id,
            role=invitation.invited_role,
        )

        member = WorkspaceMemberService.add_member(
            db, invitation.workspace_id, member_data
        )

        if member:
            # Mark invitation as accepted
            invitation.accepted_at = datetime.utcnow()
            db.commit()

        return member

    @staticmethod
    def accept_invitation_by_token(
        db: Session,
        token: str,
        user_id: uuid.UUID,
    ) -> Optional[WorkspaceMember]:
        """
        Accept a workspace invitation using the raw token string.
        
        Args:
            db: Database session
            token: Raw invitation token from magic link
            user_id: User UUID accepting invitation
            
        Returns:
            Created WorkspaceMember or None if invitation invalid/expired
        """
        # Hash the token to match stored hash
        token_hash = hash(token)  # In production, use proper hash function
        
        # Find invitation by token hash
        invitation = db.scalar(
            select(WorkspaceInvitation).where(
                and_(
                    WorkspaceInvitation.token_hash == token_hash,
                    WorkspaceInvitation.accepted_at.is_(None),
                    WorkspaceInvitation.expires_at > datetime.utcnow(),
                )
            )
        )

        if not invitation:
            return None
        
        # Add as member with invitation role
        member_data = WorkspaceMemberCreate(
            user_id=user_id,
            role=invitation.invited_role,
        )

        member = WorkspaceMemberService.add_member(
            db, invitation.workspace_id, member_data
        )

        if member:
            # Mark invitation as accepted
            invitation.accepted_at = datetime.utcnow()
            db.commit()

        return member

    @staticmethod
    def cancel_invitation(
        db: Session,
        invitation_id: uuid.UUID,
    ) -> bool:
        """
        Cancel a pending invitation.
        
        Args:
            db: Database session
            invitation_id: Invitation UUID
            
        Returns:
            True if cancelled, False if not found or already accepted
        """
        invitation = WorkspaceInvitationService.get_invitation(db, invitation_id)
        if not invitation or invitation.accepted_at is not None:
            return False

        db.delete(invitation)
        db.commit()
        return True


class WorkspaceAccessLogService:
    """Service for workspace access logging"""

    @staticmethod
    def log_access(
        db: Session,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> WorkspaceAccessLog:
        """
        Log a user's access to workspace (context switch).
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            user_id: User UUID
            
        Returns:
            Created WorkspaceAccessLog
        """
        access_log = WorkspaceAccessLog(
            workspace_id=workspace_id,
            user_id=user_id,
        )

        db.add(access_log)
        db.commit()
        db.refresh(access_log)

        return access_log

    @staticmethod
    def get_access_history(
        db: Session,
        workspace_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[WorkspaceAccessLog], int]:
        """
        Get access history for a workspace.
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            user_id: Optional filter by user
            skip: Number to skip
            limit: Max records
            
        Returns:
            Tuple of (logs list, total count)
        """
        filters = [WorkspaceAccessLog.workspace_id == workspace_id]
        if user_id:
            filters.append(WorkspaceAccessLog.user_id == user_id)

        count_stmt = select(func.count(WorkspaceAccessLog.id)).where(and_(*filters))

        stmt = (
            select(WorkspaceAccessLog)
            .where(and_(*filters))
            .order_by(WorkspaceAccessLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        logs = db.scalars(stmt).all()
        total = db.scalar(count_stmt)

        return logs, total

    @staticmethod
    def get_last_accessed_workspace(
        db: Session,
        user_id: uuid.UUID,
    ) -> Optional[Workspace]:
        """
        Get the user's last accessed workspace.
        
        Module 2 - AC 2: State Persistence
        Returns the workspace that was most recently accessed by the user.
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            Last accessed Workspace or None
        """
        # Get most recent access log
        stmt = (
            select(WorkspaceAccessLog)
            .where(WorkspaceAccessLog.user_id == user_id)
            .order_by(WorkspaceAccessLog.created_at.desc())
            .limit(1)
        )
        
        last_access = db.scalar(stmt)
        
        if not last_access:
            return None
        
        # Get the workspace
        return WorkspaceService.get_workspace(db, last_access.workspace_id)


class WorkspaceSettingService:
    """Service for workspace settings management"""

    @staticmethod
    def get_settings(
        db: Session,
        workspace_id: uuid.UUID,
    ) -> Optional[WorkspaceSetting]:
        """
        Get workspace settings.
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            
        Returns:
            WorkspaceSetting or None
        """
        stmt = select(WorkspaceSetting).where(WorkspaceSetting.workspace_id == workspace_id)
        return db.scalar(stmt)

    @staticmethod
    def update_settings(
        db: Session,
        workspace_id: uuid.UUID,
        update_data: WorkspaceSettingUpdate,
    ) -> Optional[WorkspaceSetting]:
        """
        Update workspace settings.
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            update_data: Update data
            
        Returns:
            Updated WorkspaceSetting or None if not found
        """
        settings = WorkspaceSettingService.get_settings(db, workspace_id)
        if not settings:
            return None

        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        db.commit()
        db.refresh(settings)
        return settings
