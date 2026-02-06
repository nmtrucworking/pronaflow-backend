"""
Project Repository
Handles all database operations for Project model.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime
import uuid

from app.repositories.base import BaseRepository
from app.models.projects import Project
from app.models.workspaces import Workspace, WorkspaceMember
from app.db.enums import ProjectStatus, ProjectVisibility


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project model with advanced querying."""
    
    def __init__(self, db: Session):
        super().__init__(Project, db)
    
    # ==================== PROJECT QUERIES ====================
    
    def get_by_name(self, workspace_id: uuid.UUID, name: str) -> Optional[Project]:
        """
        Get project by name within workspace.
        
        Args:
            workspace_id: Workspace ID
            name: Project name
            
        Returns:
            Project instance or None if not found
        """
        return (
            self.db.query(Project)
            .filter(
                and_(
                    Project.workspace_id == workspace_id,
                    Project.name == name
                )
            )
            .first()
        )
    
    def get_workspace_projects(
        self,
        workspace_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[Project]:
        """
        Get all projects in a workspace.
        
        Args:
            workspace_id: Workspace ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Include soft-deleted projects
            
        Returns:
            List of projects
        """
        query = self.db.query(Project).filter(Project.workspace_id == workspace_id)
        
        if not include_deleted:
            query = query.filter(Project.is_deleted == False)
        
        return query.offset(skip).limit(limit).all()
    
    def get_user_projects(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """
        Get all projects where user is owner or member.
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of projects
        """
        return (
            self.db.query(Project)
            .filter(Project.owner_id == user_id)
            .filter(Project.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_status(
        self,
        workspace_id: uuid.UUID,
        status: ProjectStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """
        Get projects by status.
        
        Args:
            workspace_id: Workspace ID
            status: Project status
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of projects with given status
        """
        return (
            self.db.query(Project)
            .filter(
                and_(
                    Project.workspace_id == workspace_id,
                    Project.status == status,
                    Project.is_deleted == False
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_projects(
        self,
        workspace_id: uuid.UUID,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Project]:
        """
        Search projects by name or description.
        
        Args:
            workspace_id: Workspace ID
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching projects
        """
        return (
            self.db.query(Project)
            .filter(Project.workspace_id == workspace_id)
            .filter(
                or_(
                    Project.name.ilike(f"%{query}%"),
                    Project.description.ilike(f"%{query}%")
                )
            )
            .filter(Project.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    # ==================== STATUS MANAGEMENT ====================
    
    def update_status(
        self,
        project_id: uuid.UUID,
        status: ProjectStatus
    ) -> Optional[Project]:
        """
        Update project status.
        
        Args:
            project_id: Project ID
            status: New project status
            
        Returns:
            Updated project or None if not found
        """
        project = self.get_by_id(project_id)
        if project:
            project.status = status
            self.db.commit()
            self.db.refresh(project)
        return project
    
    def get_active_projects(
        self,
        workspace_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """
        Get all active (in progress) projects.
        
        Args:
            workspace_id: Workspace ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active projects
        """
        return (
            self.db.query(Project)
            .filter(
                and_(
                    Project.workspace_id == workspace_id,
                    Project.status.in_([
                        ProjectStatus.NOT_STARTED,
                        ProjectStatus.IN_PROGRESS,
                        ProjectStatus.IN_REVIEW
                    ]),
                    Project.is_deleted == False
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_completed_projects(
        self,
        workspace_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """
        Get all completed projects.
        
        Args:
            workspace_id: Workspace ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of completed projects
        """
        return (
            self.db.query(Project)
            .filter(
                and_(
                    Project.workspace_id == workspace_id,
                    Project.status.in_([
                        ProjectStatus.DONE,
                        ProjectStatus.CANCELLED
                    ]),
                    Project.is_deleted == False
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    # ==================== OWNERSHIP & ACCESS ====================
    
    def is_owner(self, project_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Check if user is project owner.
        
        Args:
            project_id: Project ID
            user_id: User ID
            
        Returns:
            True if user is owner, False otherwise
        """
        project = self.get_by_id(project_id)
        return project.owner_id == user_id if project else False
    
    def can_access(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """
        Check if user can access project (owner or workspace member).
        
        Args:
            project_id: Project ID
            user_id: User ID
            
        Returns:
            True if user can access, False otherwise
        """
        project = self.get_by_id(project_id)
        if not project:
            return False
        
        # Owner can always access
        if project.owner_id == user_id:
            return True
        
        # Check if user is workspace member for private projects
        workspace_member = (
            self.db.query(WorkspaceMember)
            .filter(
                and_(
                    WorkspaceMember.workspace_id == project.workspace_id,
                    WorkspaceMember.user_id == user_id
                )
            )
            .first()
        )
        
        return workspace_member is not None
    
    def change_owner(
        self,
        project_id: uuid.UUID,
        new_owner_id: uuid.UUID
    ) -> Optional[Project]:
        """
        Change project owner.
        
        Args:
            project_id: Project ID
            new_owner_id: New owner's user ID
            
        Returns:
            Updated project or None if not found
        """
        project = self.get_by_id(project_id)
        if project:
            project.owner_id = new_owner_id
            self.db.commit()
            self.db.refresh(project)
        return project
    
    # ==================== STATISTICS ====================
    
    def count_by_status(self, workspace_id: uuid.UUID, status: ProjectStatus) -> int:
        """
        Count projects by status.
        
        Args:
            workspace_id: Workspace ID
            status: Project status
            
        Returns:
            Number of projects with given status
        """
        return (
            self.db.query(func.count(Project.id))
            .filter(
                and_(
                    Project.workspace_id == workspace_id,
                    Project.status == status,
                    Project.is_deleted == False
                )
            )
            .scalar() or 0
        )
    
    def get_status_distribution(self, workspace_id: uuid.UUID) -> Dict[str, int]:
        """
        Get distribution of projects by status.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            Dictionary with status: count pairs
        """
        results = (
            self.db.query(
                Project.status,
                func.count(Project.id).label('count')
            )
            .filter(
                and_(
                    Project.workspace_id == workspace_id,
                    Project.is_deleted == False
                )
            )
            .group_by(Project.status)
            .all()
        )
        
        return {
            str(status): count
            for status, count in results
        }
    
    def get_workspace_stats(self, workspace_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get comprehensive workspace project statistics.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            Dictionary with project statistics
        """
        total = (
            self.db.query(func.count(Project.id))
            .filter(
                and_(
                    Project.workspace_id == workspace_id,
                    Project.is_deleted == False
                )
            )
            .scalar() or 0
        )
        
        return {
            "total_projects": total,
            "not_started": self.count_by_status(workspace_id, ProjectStatus.NOT_STARTED),
            "in_progress": self.count_by_status(workspace_id, ProjectStatus.IN_PROGRESS),
            "in_review": self.count_by_status(workspace_id, ProjectStatus.IN_REVIEW),
            "done": self.count_by_status(workspace_id, ProjectStatus.DONE),
            "cancelled": self.count_by_status(workspace_id, ProjectStatus.CANCELLED),
        }
    
    def count_user_projects(self, user_id: uuid.UUID) -> int:
        """
        Count projects owned by user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of projects
        """
        return (
            self.db.query(func.count(Project.id))
            .filter(
                and_(
                    Project.owner_id == user_id,
                    Project.is_deleted == False
                )
            )
            .scalar() or 0
        )
