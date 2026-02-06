"""
Project Service - Business logic for project operations
"""
from typing import Optional, List
from sqlalchemy.orm import Session
import uuid
from datetime import date

from app.repositories.project_repository import ProjectRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.models.projects import Project
from app.db.enums import ProjectStatus, WorkspaceRole
from app.utils.exceptions import (
    NotFoundException,
    ForbiddenException,
    ConflictException,
    DuplicateException,
)


class ProjectService:
    """Service for project operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.workspace_repo = WorkspaceRepository(db)
    
    # ==================== PROJECT MANAGEMENT ====================
    
    def create_project(
        self,
        workspace_id: uuid.UUID,
        owner_id: uuid.UUID,
        user_id: uuid.UUID,
        name: str,
        description: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> Project:
        """
        Create a new project.
        
        Args:
            workspace_id: Workspace ID
            owner_id: Project owner ID
            user_id: Current user ID (for authorization)
            name: Project name
            description: Optional description
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            Created project
            
        Raises:
            NotFoundException: If workspace not found
            ForbiddenException: If not authorized
            DuplicateException: If name already exists
        """
        # Check workspace exists
        workspace = self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundException("Workspace not found")
        
        # Check authorization (must be workspace member)
        if not self.workspace_repo.is_member(workspace_id, user_id):
            raise ForbiddenException("You are not a member of this workspace")
        
        # Check for duplicate name in workspace
        existing = self.project_repo.get_by_name(workspace_id, name)
        if existing:
            raise DuplicateException(f"Project '{name}' already exists in this workspace")
        
        # Create project
        project_data = {
            "workspace_id": workspace_id,
            "owner_id": owner_id,
            "name": name,
            "status": ProjectStatus.NOT_STARTED,
        }
        if description:
            project_data["description"] = description
        if start_date:
            project_data["start_date"] = start_date
        if end_date:
            project_data["end_date"] = end_date
        
        project = self.project_repo.create(project_data)
        return project
    
    def update_project(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[ProjectStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> Project:
        """
        Update project details.
        
        Args:
            project_id: Project ID
            user_id: Current user ID (for authorization)
            name: New name
            description: New description
            status: New status
            start_date: New start date
            end_date: New end date
            
        Returns:
            Updated project
            
        Raises:
            NotFoundException: If project not found
            ForbiddenException: If not authorized
        """
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project not found")
        
        # Check authorization (owner only)
        if project.owner_id != user_id:
            raise ForbiddenException("Only project owner can update")
        
        # Check for duplicate name if changing
        if name and name != project.name:
            existing = self.project_repo.get_by_name(project.workspace_id, name)
            if existing:
                raise DuplicateException(f"Project name '{name}' already in use")
        
        # Build update data
        update_data = {}
        if name:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if status:
            update_data["status"] = status
        if start_date is not None:
            update_data["start_date"] = start_date
        if end_date is not None:
            update_data["end_date"] = end_date
        
        if update_data:
            project = self.project_repo.update(project_id, update_data)
        
        return project
    
    def delete_project(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """
        Delete a project (soft delete).
        
        Args:
            project_id: Project ID
            user_id: Current user ID (for authorization)
            
        Returns:
            True if deleted
            
        Raises:
            NotFoundException: If project not found
            ForbiddenException: If not authorized
        """
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project not found")
        
        # Check authorization
        if project.owner_id != user_id:
            raise ForbiddenException("Only project owner can delete")
        
        return self.project_repo.delete(project_id, soft=True)
    
    # ==================== PROJECT QUERIES ====================
    
    def get_project(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Project:
        """
        Get project details.
        
        Args:
            project_id: Project ID
            user_id: Current user ID (for authorization)
            
        Returns:
            Project details
            
        Raises:
            NotFoundException: If project not found
            ForbiddenException: If not authorized
        """
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project not found")
        
        # Check access (workspace member)
        if not self.project_repo.can_access(project_id, user_id):
            raise ForbiddenException("You don't have access to this project")
        
        return project
    
    def list_workspace_projects(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Project], int]:
        """
        List projects in a workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: Current user ID (for authorization)
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            Tuple of (projects, total)
            
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
            raise ForbiddenException("You are not a member of this workspace")
        
        projects = self.project_repo.get_workspace_projects(
            workspace_id,
            skip=skip,
            limit=limit
        )
        total = self.project_repo.count()
        
        return projects, total
    
    def list_user_projects(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Project], int]:
        """
        List projects owned by user.
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            Tuple of (projects, total)
        """
        projects = self.project_repo.get_user_projects(
            user_id,
            skip=skip,
            limit=limit
        )
        total = self.project_repo.count_user_projects(user_id)
        
        return projects, total
    
    def search_projects(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Project], int]:
        """
        Search projects in workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: Current user ID (for authorization)
            query: Search query
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            Tuple of (projects, total)
            
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
            raise ForbiddenException("You are not a member of this workspace")
        
        projects = self.project_repo.search_projects(
            workspace_id,
            query,
            skip=skip,
            limit=limit
        )
        
        return projects, len(projects)
    
    def get_by_status(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        status: ProjectStatus,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Project], int]:
        """
        Get projects by status.
        
        Args:
            workspace_id: Workspace ID
            user_id: Current user ID (for authorization)
            status: Project status
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            Tuple of (projects, total)
            
        Raises:
            NotFoundException: If workspace not found
            ForbiddenException: If not authorized
        """
        # Check access
        if not self.workspace_repo.is_member(workspace_id, user_id):
            raise ForbiddenException("You are not a member of this workspace")
        
        projects = self.project_repo.get_by_status(
            workspace_id,
            status,
            skip=skip,
            limit=limit
        )
        total = self.project_repo.count_by_status(workspace_id, status)
        
        return projects, total
    
    # ==================== STATUS MANAGEMENT ====================
    
    def update_status(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        status: ProjectStatus
    ) -> Project:
        """
        Update project status.
        
        Args:
            project_id: Project ID
            user_id: Current user ID (for authorization)
            status: New status
            
        Returns:
            Updated project
            
        Raises:
            NotFoundException: If project not found
            ForbiddenException: If not authorized
        """
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project not found")
        
        # Check authorization
        if project.owner_id != user_id:
            raise ForbiddenException("Only project owner can update status")
        
        return self.project_repo.update_status(project_id, status)
    
    # ==================== STATISTICS ====================
    
    def get_stats(self, project_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        """
        Get project statistics.
        
        Args:
            project_id: Project ID
            user_id: Current user ID (for authorization)
            
        Returns:
            Project statistics dictionary
            
        Raises:
            NotFoundException: If project not found
            ForbiddenException: If not authorized
        """
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project not found")
        
        # Check access
        if not self.project_repo.can_access(project_id, user_id):
            raise ForbiddenException("You don't have access to this project")
        
        return self.project_repo.get_workspace_stats(project.workspace_id)
