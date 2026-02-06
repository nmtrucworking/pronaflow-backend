"""
Workspace Repository
Handles all database operations for Workspace and WorkspaceMember models.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime
import uuid

from app.repositories.base import BaseRepository
from app.models.workspaces import Workspace, WorkspaceMember, WorkspaceInvitation, WorkspaceSetting
from app.models.users import User
from app.db.enums import WorkspaceRole


class WorkspaceRepository(BaseRepository[Workspace]):
    """Repository for Workspace model with multi-tenancy support."""
    
    def __init__(self, db: Session):
        super().__init__(Workspace, db)
    
    # ==================== WORKSPACE QUERIES ====================
    
    def get_by_name(self, name: str) -> Optional[Workspace]:
        """
        Get workspace by name.
        
        Args:
            name: Workspace name
            
        Returns:
            Workspace instance or None if not found
        """
        return self.db.query(Workspace).filter(Workspace.name == name).first()
    
    def get_by_owner(
        self,
        owner_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Workspace]:
        """
        Get all workspaces owned by a user.
        
        Args:
            owner_id: Owner user ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of workspaces
        """
        return (
            self.db.query(Workspace)
            .filter(Workspace.owner_id == owner_id)
            .filter(Workspace.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_active_workspaces(self, skip: int = 0, limit: int = 100) -> List[Workspace]:
        """
        Get all active (non-deleted) workspaces.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active workspaces
        """
        return (
            self.db.query(Workspace)
            .filter(Workspace.status == 'ACTIVE')
            .filter(Workspace.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_workspaces(
        self,
        query: str,
        user_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Workspace]:
        """
        Search workspaces by name or description.
        
        Args:
            query: Search query string
            user_id: Optional user ID to filter by membership
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching workspaces
        """
        db_query = self.db.query(Workspace).filter(
            or_(
                Workspace.name.ilike(f"%{query}%"),
                Workspace.description.ilike(f"%{query}%")
            )
        ).filter(Workspace.is_deleted == False)
        
        if user_id:
            # Filter by workspaces where user is member or owner
            db_query = db_query.join(WorkspaceMember).filter(
                or_(
                    Workspace.owner_id == user_id,
                    WorkspaceMember.user_id == user_id
                )
            )
        
        return db_query.offset(skip).limit(limit).all()
    
    # ==================== MEMBERSHIP QUERIES ====================
    
    def get_user_workspaces(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Workspace]:
        """
        Get all workspaces where user is a member or owner.
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of workspaces
        """
        return (
            self.db.query(Workspace)
            .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
            .filter(
                or_(
                    Workspace.owner_id == user_id,
                    WorkspaceMember.user_id == user_id
                )
            )
            .filter(Workspace.is_deleted == False)
            .distinct()
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_workspace_members(
        self,
        workspace_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkspaceMember]:
        """
        Get all members of a workspace.
        
        Args:
            workspace_id: Workspace ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of workspace members
        """
        return (
            self.db.query(WorkspaceMember)
            .filter(WorkspaceMember.workspace_id == workspace_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_member(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[WorkspaceMember]:
        """
        Get specific workspace member.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            
        Returns:
            WorkspaceMember instance or None if not found
        """
        return (
            self.db.query(WorkspaceMember)
            .filter(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id
                )
            )
            .first()
        )
    
    def add_member(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        role: WorkspaceRole = WorkspaceRole.MEMBER
    ) -> WorkspaceMember:
        """
        Add a user to workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            role: Workspace role
            
        Returns:
            Created WorkspaceMember instance
        """
        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member
    
    def remove_member(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """
        Remove a user from workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            
        Returns:
            True if removed, False if member not found
        """
        member = self.get_member(workspace_id, user_id)
        if member:
            self.db.delete(member)
            self.db.commit()
            return True
        return False
    
    def update_member_role(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        role: WorkspaceRole
    ) -> Optional[WorkspaceMember]:
        """
        Update workspace member's role.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            role: New workspace role
            
        Returns:
            Updated WorkspaceMember instance or None if not found
        """
        member = self.get_member(workspace_id, user_id)
        if member:
            member.role = role
            self.db.commit()
            self.db.refresh(member)
        return member
    
    # ==================== PERMISSION CHECKS ====================
    
    def is_member(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Check if user is a member of workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            
        Returns:
            True if user is member, False otherwise
        """
        workspace = self.get_by_id(workspace_id)
        if not workspace:
            return False
        
        # Owner is always a member
        if workspace.owner_id == user_id:
            return True
        
        # Check membership
        member = self.get_member(workspace_id, user_id)
        return member is not None
    
    def is_owner(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Check if user is the owner of workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            
        Returns:
            True if user is owner, False otherwise
        """
        workspace = self.get_by_id(workspace_id)
        return workspace.owner_id == user_id if workspace else False
    
    def is_admin(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Check if user is an admin of workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            
        Returns:
            True if user is admin or owner, False otherwise
        """
        if self.is_owner(workspace_id, user_id):
            return True
        
        member = self.get_member(workspace_id, user_id)
        return member.role == WorkspaceRole.ADMIN if member else False
    
    def get_user_role(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[WorkspaceRole]:
        """
        Get user's role in workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            
        Returns:
            WorkspaceRole or None if not a member
        """
        if self.is_owner(workspace_id, user_id):
            return WorkspaceRole.OWNER
        
        member = self.get_member(workspace_id, user_id)
        return member.role if member else None
    
    def has_permission(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        required_role: WorkspaceRole
    ) -> bool:
        """
        Check if user has required permission level.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            required_role: Minimum required role
            
        Returns:
            True if user has permission, False otherwise
        """
        user_role = self.get_user_role(workspace_id, user_id)
        if not user_role:
            return False
        
        # Role hierarchy: OWNER > ADMIN > MEMBER > VIEWER
        role_hierarchy = {
            WorkspaceRole.OWNER: 4,
            WorkspaceRole.ADMIN: 3,
            WorkspaceRole.MEMBER: 2,
            WorkspaceRole.VIEWER: 1
        }
        
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
    
    # ==================== WORKSPACE SETTINGS ====================
    
    def get_settings(self, workspace_id: uuid.UUID) -> Optional[WorkspaceSetting]:
        """
        Get workspace settings.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            WorkspaceSetting instance or None if not found
        """
        return (
            self.db.query(WorkspaceSetting)
            .filter(WorkspaceSetting.workspace_id == workspace_id)
            .first()
        )
    
    def update_settings(
        self,
        workspace_id: uuid.UUID,
        settings_data: Dict[str, Any]
    ) -> WorkspaceSetting:
        """
        Update workspace settings.
        
        Args:
            workspace_id: Workspace ID
            settings_data: Dictionary with settings data
            
        Returns:
            Updated or created WorkspaceSetting instance
        """
        settings = self.get_settings(workspace_id)
        
        if settings:
            # Update existing settings
            for key, value in settings_data.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
        else:
            # Create new settings
            settings = WorkspaceSetting(
                workspace_id=workspace_id,
                **settings_data
            )
            self.db.add(settings)
        
        self.db.commit()
        self.db.refresh(settings)
        return settings
    
    # ==================== STATISTICS ====================
    
    def count_members(self, workspace_id: uuid.UUID) -> int:
        """
        Count number of members in workspace.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            Number of members (including owner)
        """
        return (
            self.db.query(func.count(WorkspaceMember.id))
            .filter(WorkspaceMember.workspace_id == workspace_id)
            .scalar() or 0
        ) + 1  # +1 for owner
    
    def count_by_role(self, workspace_id: uuid.UUID, role: WorkspaceRole) -> int:
        """
        Count members by role.
        
        Args:
            workspace_id: Workspace ID
            role: Workspace role
            
        Returns:
            Number of members with given role
        """
        return (
            self.db.query(func.count(WorkspaceMember.id))
            .filter(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.role == role
                )
            )
            .scalar() or 0
        )
    
    def get_workspace_stats(self, workspace_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get comprehensive workspace statistics.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            Dictionary with workspace statistics
        """
        workspace = self.get_by_id(workspace_id)
        if not workspace:
            return {}
        
        return {
            "total_members": self.count_members(workspace_id),
            "admins": self.count_by_role(workspace_id, WorkspaceRole.ADMIN),
            "members": self.count_by_role(workspace_id, WorkspaceRole.MEMBER),
            "viewers": self.count_by_role(workspace_id, WorkspaceRole.VIEWER),
            "created_at": workspace.created_at,
            "status": workspace.status
        }
