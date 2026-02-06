"""
Workspace Service - Business logic for workspace operations
"""
from typing import Optional, List
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.user_repository import UserRepository
from app.models.workspaces import Workspace, WorkspaceMember
from app.db.enums import WorkspaceRole
from app.utils.exceptions import (
    NotFoundException,
    ForbiddenException,
    ConflictException,
    DuplicateException,
)


class WorkspaceService:
    """Service for workspace operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.workspace_repo = WorkspaceRepository(db)
        self.user_repo = UserRepository(db)
    
    # ==================== WORKSPACE MANAGEMENT ====================
    
    def create_workspace(
        self,
        name: str,
        owner_id: uuid.UUID,
        description: Optional[str] = None
    ) -> Workspace:
        """
        Create a new workspace.
        
        Args:
            name: Workspace name
            owner_id: Owner user ID
            description: Optional description
            
        Returns:
            Created workspace
            
        Raises:
            NotFoundException: If owner not found
            ConflictException: If name already exists
        """
        # Verify owner exists
        owner = self.user_repo.get_by_id(owner_id)
        if not owner:
            raise NotFoundException("Owner user not found")
        
        # Check for duplicate name
        existing = self.workspace_repo.get_by_name(name)
        if existing:
            raise DuplicateException(f"Workspace with name '{name}' already exists")
        
        # Create workspace
        workspace_data = {
            "name": name,
            "owner_id": owner_id,
            "status": "ACTIVE",
        }
        if description:
            workspace_data["description"] = description
        
        workspace = self.workspace_repo.create(workspace_data)
        return workspace
    
    def update_workspace(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Workspace:
        """
        Update workspace details.
        
        Args:
            workspace_id: Workspace ID
            user_id: Current user ID (for authorization)
            name: New name
            description: New description
            
        Returns:
            Updated workspace
            
        Raises:
            NotFoundException: If workspace not found
            ForbiddenException: If user not owner
        """
        workspace = self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundException("Workspace not found")
        
        # Check authorization
        if workspace.owner_id != user_id:
            raise ForbiddenException("Only workspace owner can update settings")
        
        # Check for duplicate name if changing
        if name and name != workspace.name:
            existing = self.workspace_repo.get_by_name(name)
            if existing:
                raise DuplicateException(f"Workspace name '{name}' already in use")
        
        # Update fields
        update_data = {}
        if name:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        
        if update_data:
            workspace = self.workspace_repo.update(workspace_id, update_data)
        
        return workspace
    
    def delete_workspace(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """
        Delete a workspace (soft delete).
        
        Args:
            workspace_id: Workspace ID
            user_id: Current user ID (for authorization)
            
        Returns:
            True if deleted
            
        Raises:
            NotFoundException: If workspace not found
            ForbiddenException: If user not owner
        """
        workspace = self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundException("Workspace not found")
        
        # Check authorization
        if workspace.owner_id != user_id:
            raise ForbiddenException("Only workspace owner can delete")
        
        # Soft delete
        return self.workspace_repo.delete(workspace_id, soft=True)
    
    # ==================== WORKSPACE QUERIES ====================
    
    def get_workspace(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Workspace:
        """
        Get workspace details.
        
        Args:
            workspace_id: Workspace ID
            user_id: Current user ID (for authorization check)
            
        Returns:
            Workspace details
            
        Raises:
            NotFoundException: If workspace not found
            ForbiddenException: If user not a member
        """
        workspace = self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundException("Workspace not found")
        
        # Check access
        if not self.workspace_repo.is_member(workspace_id, user_id):
            raise ForbiddenException("You don't have access to this workspace")
        
        return workspace
    
    def list_user_workspaces(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Workspace], int]:
        """
        List all workspaces for a user.
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            Tuple of (workspaces, total)
        """
        workspaces = self.workspace_repo.get_user_workspaces(
            user_id,
            skip=skip,
            limit=limit
        )
        total = self.workspace_repo.count()
        return workspaces, total
    
    def search_workspaces(
        self,
        query: str,
        user_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Workspace], int]:
        """
        Search workspaces.
        
        Args:
            query: Search query
            user_id: Optional user ID to filter by membership
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            Tuple of (workspaces, total)
        """
        workspaces = self.workspace_repo.search_workspaces(
            query,
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        total = len(workspaces)  # Simple count for search
        return workspaces, total
    
    # ==================== MEMBER MANAGEMENT ====================
    
    def add_member(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        new_member_id: uuid.UUID,
        role: WorkspaceRole = WorkspaceRole.MEMBER
    ) -> WorkspaceMember:
        """
        Add a member to workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: Current user ID (for authorization)
            new_member_id: User ID to add
            role: Role to assign
            
        Returns:
            Created membership
            
        Raises:
            NotFoundException: If workspace or user not found
            ForbiddenException: If not authorized
            DuplicateException: If user already member
        """
        # Check workspace exists
        workspace = self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundException("Workspace not found")
        
        # Check authorization (admin or owner)
        if not self.workspace_repo.has_permission(
            workspace_id,
            user_id,
            WorkspaceRole.ADMIN
        ):
            raise ForbiddenException("Only admins can add members")
        
        # Check new member exists
        new_member = self.user_repo.get_by_id(new_member_id)
        if not new_member:
            raise NotFoundException("User to add not found")
        
        # Check not already member
        existing = self.workspace_repo.get_member(workspace_id, new_member_id)
        if existing:
            raise DuplicateException("User is already a member")
        
        # Add member
        return self.workspace_repo.add_member(
            workspace_id,
            new_member_id,
            role=role
        )
    
    def remove_member(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        member_id: uuid.UUID
    ) -> bool:
        """
        Remove a member from workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: Current user ID (for authorization)
            member_id: User ID to remove
            
        Returns:
            True if removed
            
        Raises:
            NotFoundException: If workspace not found
            ForbiddenException: If not authorized
        """
        # Check workspace exists
        workspace = self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundException("Workspace not found")
        
        # Check authorization
        if not self.workspace_repo.has_permission(
            workspace_id,
            user_id,
            WorkspaceRole.ADMIN
        ):
            raise ForbiddenException("Only admins can remove members")
        
        # Can't remove owner
        if workspace.owner_id == member_id:
            raise ConflictException("Cannot remove workspace owner")
        
        return self.workspace_repo.remove_member(workspace_id, member_id)
    
    def update_member_role(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        member_id: uuid.UUID,
        role: WorkspaceRole
    ) -> WorkspaceMember:
        """
        Update member's role.
        
        Args:
            workspace_id: Workspace ID
            user_id: Current user ID (for authorization)
            member_id: Member to update
            role: New role
            
        Returns:
            Updated membership
            
        Raises:
            NotFoundException: If workspace or member not found
            ForbiddenException: If not authorized
        """
        # Check workspace exists
        workspace = self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundException("Workspace not found")
        
        # Check authorization
        if not self.workspace_repo.has_permission(
            workspace_id,
            user_id,
            WorkspaceRole.ADMIN
        ):
            raise ForbiddenException("Only admins can update member roles")
        
        # Can't change owner's role
        if workspace.owner_id == member_id:
            raise ConflictException("Cannot change owner's role")
        
        return self.workspace_repo.update_member_role(
            workspace_id,
            member_id,
            role
        )
    
    def get_members(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[WorkspaceMember], int]:
        """
        Get workspace members.
        
        Args:
            workspace_id: Workspace ID
            user_id: Current user ID (for authorization)
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            Tuple of (members, total)
            
        Raises:
            NotFoundException: If workspace not found
            ForbiddenException: If not authorized
        """
        # Check workspace exists
        workspace = self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundException("Workspace not found")
        
        # Check access
        if not self.workspace_repo.is_member(workspace_id, user_id):
            raise ForbiddenException("You don't have access to this workspace")
        
        members = self.workspace_repo.get_workspace_members(
            workspace_id,
            skip=skip,
            limit=limit
        )
        total = self.workspace_repo.count_members(workspace_id)
        
        return members, total
    
    # ==================== STATISTICS ====================
    
    def get_stats(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        """
        Get workspace statistics.
        
        Args:
            workspace_id: Workspace ID
            user_id: Current user ID (for authorization)
            
        Returns:
            Workspace statistics dictionary
            
        Raises:
            NotFoundException: If workspace not found
            ForbiddenException: If not authorized
        """
        # Check workspace exists
        workspace = self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundException("Workspace not found")
        
        # Check access
        if not self.workspace_repo.is_member(workspace_id, user_id):
            raise ForbiddenException("You don't have access to this workspace")
        
        return self.workspace_repo.get_workspace_stats(workspace_id)
