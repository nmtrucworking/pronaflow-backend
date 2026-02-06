"""
Service layer for Project management.
Handles business logic for Functional Module 3: Project Lifecycle Management.
Ref: docs/01-Requirements/Functional-Modules/3 - Project Lifecycle Management.md
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any

from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.projects import Project
from app.models.projects_extended import (
    ProjectMember,
    ProjectTemplate,
    ProjectBaseline,
    ProjectChangeRequest,
    ProjectArchive,
)
from app.models.users import User
from app.models.workspaces import WorkspaceMember
from app.db.enums import (
    ProjectStatus,
    ProjectRole,
    ProjectGovernanceMode,
    WorkspaceRole,
    ChangeRequestStatus,
    ProjectHealthStatus,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectStatusUpdate,
    ProjectMemberCreate,
    ProjectMemberUpdate,
    ProjectTemplateCreate,
    ProjectTemplateUpdate,
    ProjectBaselineCreate,
    ChangeRequestCreate,
    ChangeRequestUpdate,
    ChangeRequestApprove,
    ProjectClone,
    ProjectHealthUpdate,
)


class ProjectService:
    """Service for project CRUD operations"""

    @staticmethod
    def create_project(
        db: Session,
        project_data: ProjectCreate,
        owner_id: uuid.UUID,
    ) -> Project:
        """
        Create a new project.
        
        Args:
            db: Database session
            project_data: Project creation data
            owner_id: UUID of project owner (current user)
            
        Returns:
            Created project object
            
        Ref: Module 3 - Feature 2.1 - AC 1
        """
        # Validate workspace membership
        workspace_member = db.scalar(
            select(WorkspaceMember).where(
                and_(
                    WorkspaceMember.workspace_id == project_data.workspace_id,
                    WorkspaceMember.user_id == owner_id,
                    WorkspaceMember.is_active == True,
                )
            )
        )
        
        if not workspace_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of this workspace"
            )

        # Create project
        project = Project(
            workspace_id=project_data.workspace_id,
            owner_id=owner_id,
            name=project_data.name.strip(),
            description=project_data.description,
            start_date=project_data.start_date,
            end_date=project_data.end_date,
            status=ProjectStatus.NOT_STARTED,
            governance_mode=project_data.governance_mode,
            visibility=project_data.visibility,
            priority=project_data.priority,
        )

        db.add(project)
        db.flush()

        # Automatically add owner as PROJECT_MANAGER
        owner_member = ProjectMember(
            project_id=project.id,
            user_id=owner_id,
            role=ProjectRole.MANAGER,
            joined_at=datetime.utcnow(),
        )
        db.add(owner_member)

        # If STRICT mode, create initial baseline placeholder
        if project_data.governance_mode == ProjectGovernanceMode.STRICT:
            # Note: Actual baseline created when transitioning to IN_PROGRESS
            pass

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_project(
        db: Session,
        project_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
    ) -> Optional[Project]:
        """
        Get a project by ID with permission check.
        
        Args:
            db: Database session
            project_id: Project UUID
            user_id: Optional user ID for permission check
            
        Returns:
            Project object or None if not found/no access
        """
        project = db.scalar(
            select(Project).where(
                and_(
                    Project.id == project_id,
                    Project.is_deleted == False,
                )
            )
        )

        if not project:
            return None

        # Check visibility and membership
        if user_id:
            # Check if user is workspace admin or project member
            is_workspace_admin = ProjectService._is_workspace_admin(
                db, project.workspace_id, user_id
            )
            is_project_member = ProjectService._is_project_member(
                db, project_id, user_id
            )

            # For PRIVATE projects, user must be member or workspace admin
            if project.visibility == "private" and not (is_project_member or is_workspace_admin):
                return None

        return project

    @staticmethod
    def list_projects(
        db: Session,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 10,
        status_filter: Optional[ProjectStatus] = None,
        archived: bool = False,
    ) -> Tuple[List[Project], int]:
        """
        List projects in a workspace.
        
        Args:
            db: Database session
            workspace_id: Workspace UUID
            user_id: User UUID for permission filtering
            skip: Number of records to skip
            limit: Maximum records to return
            status_filter: Optional status filter
            archived: Include archived projects
            
        Returns:
            Tuple of (projects list, total count)
        """
        # Check workspace membership
        is_workspace_admin = ProjectService._is_workspace_admin(
            db, workspace_id, user_id
        )

        # Build base query
        conditions = [
            Project.workspace_id == workspace_id,
            Project.is_deleted == False,
        ]

        if status_filter:
            conditions.append(Project.status == status_filter)

        if archived:
            conditions.append(Project.archived_at.isnot(None))
        else:
            conditions.append(Project.archived_at.is_(None))

        # For non-admins, filter by visibility and membership
        if not is_workspace_admin:
            # Get user's project memberships
            user_project_ids = db.scalars(
                select(ProjectMember.project_id).where(
                    ProjectMember.user_id == user_id
                )
            ).all()

            conditions.append(
                or_(
                    Project.visibility == "public",
                    Project.id.in_(user_project_ids)
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(Project).where(and_(*conditions))
        total = db.scalar(count_stmt)

        # Get projects
        stmt = (
            select(Project)
            .where(and_(*conditions))
            .order_by(Project.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        projects = db.scalars(stmt).all()

        return list(projects), total

    @staticmethod
    def update_project(
        db: Session,
        project_id: uuid.UUID,
        project_data: ProjectUpdate,
        user_id: uuid.UUID,
    ) -> Project:
        """
        Update project information.
        
        Args:
            db: Database session
            project_id: Project UUID
            project_data: Project update data
            user_id: User ID (must be PM or workspace admin)
            
        Returns:
            Updated project object
            
        Ref: Module 3 - Feature 2.1 - AC 2
        """
        project = ProjectService.get_project(db, project_id, user_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        # Check permission - must be PM or workspace admin
        if not ProjectService._can_manage_project(db, project, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Project Manager or Workspace Admin can update project"
            )

        # Update fields
        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        project.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def update_project_status(
        db: Session,
        project_id: uuid.UUID,
        status_data: ProjectStatusUpdate,
        user_id: uuid.UUID,
    ) -> Project:
        """
        Update project status with transition validation.
        
        Args:
            db: Database session
            project_id: Project UUID
            status_data: Status update data
            user_id: User ID
            
        Returns:
            Updated project object
            
        Ref: Module 3 - Feature 2.2 - AC 2 & AC 3
        """
        project = ProjectService.get_project(db, project_id, user_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        # Check permission
        if not ProjectService._can_manage_project(db, project, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Project Manager or Workspace Admin can update status"
            )

        # Validate status transition
        ProjectService._validate_status_transition(
            db, project, status_data.status, status_data.cancellation_reason
        )

        # Update status
        project.status = status_data.status
        
        # Handle CANCELLED status
        if status_data.status == ProjectStatus.CANCELLED:
            # Store cancellation reason (could be in a separate field or metadata)
            # For now, append to description or use change request system
            pass

        # Auto-archive after DONE or CANCELLED (optional, based on settings)
        if status_data.status in [ProjectStatus.DONE, ProjectStatus.CANCELLED]:
            # Mark for archiving after 30 days (business rule)
            pass

        project.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(
        db: Session,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        soft_delete: bool = True,
    ) -> None:
        """
        Delete a project (soft or hard delete).
        
        Args:
            db: Database session
            project_id: Project UUID
            user_id: User ID
            soft_delete: If True, soft delete; if False, hard delete
            
        Ref: Module 3 - Feature 2.5 - AC 1
        """
        project = ProjectService.get_project(db, project_id, user_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        # Only PM or workspace admin can delete
        if not ProjectService._can_manage_project(db, project, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Project Manager or Workspace Admin can delete project"
            )

        if soft_delete:
            # Soft delete
            project.is_deleted = True
            project.deleted_at = datetime.utcnow()
            db.commit()
        else:
            # Hard delete (use with caution)
            db.delete(project)
            db.commit()

    @staticmethod
    def clone_project(
        db: Session,
        project_id: uuid.UUID,
        clone_data: ProjectClone,
        user_id: uuid.UUID,
    ) -> Project:
        """
        Clone/duplicate an existing project.
        
        Args:
            db: Database session
            project_id: Project UUID to clone
            clone_data: Clone configuration
            user_id: User ID
            
        Returns:
            Cloned project object
            
        Ref: Module 3 - Feature 2.1 - AC 3
        """
        source_project = ProjectService.get_project(db, project_id, user_id)
        if not source_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source project not found"
            )

        # Create new project with copied data
        new_project = Project(
            workspace_id=source_project.workspace_id,
            owner_id=user_id,
            name=clone_data.name,
            description=f"Copy of {source_project.name}",
            status=ProjectStatus.NOT_STARTED,
            governance_mode=source_project.governance_mode if clone_data.copy_structure else ProjectGovernanceMode.SIMPLE,
            visibility=source_project.visibility,
        )

        db.add(new_project)
        db.flush()

        # Add cloner as PM
        pm_member = ProjectMember(
            project_id=new_project.id,
            user_id=user_id,
            role=ProjectRole.MANAGER,
            joined_at=datetime.utcnow(),
        )
        db.add(pm_member)

        # Copy members if requested
        if clone_data.copy_members:
            source_members = db.scalars(
                select(ProjectMember).where(
                    ProjectMember.project_id == project_id
                )
            ).all()
            
            for member in source_members:
                if member.user_id != user_id:  # Skip cloner as already added
                    new_member = ProjectMember(
                        project_id=new_project.id,
                        user_id=member.user_id,
                        role=member.role,
                        joined_at=datetime.utcnow(),
                    )
                    db.add(new_member)

        # TODO: Copy task structure if clone_data.copy_structure
        # TODO: Copy tasks if clone_data.copy_tasks

        db.commit()
        db.refresh(new_project)
        return new_project

    # ===== Permission Helpers =====

    @staticmethod
    def _is_workspace_admin(db: Session, workspace_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Check if user is workspace admin or owner"""
        member = db.scalar(
            select(WorkspaceMember).where(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.is_active == True,
                    WorkspaceMember.role.in_([WorkspaceRole.OWNER, WorkspaceRole.ADMIN]),
                )
            )
        )
        return member is not None

    @staticmethod
    def _is_project_member(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Check if user is project member"""
        member = db.scalar(
            select(ProjectMember).where(
                and_(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == user_id,
                )
            )
        )
        return member is not None

    @staticmethod
    def _can_manage_project(db: Session, project: Project, user_id: uuid.UUID) -> bool:
        """Check if user can manage project (PM or workspace admin)"""
        # Check if project owner
        if project.owner_id == user_id:
            return True

        # Check if workspace admin
        if ProjectService._is_workspace_admin(db, project.workspace_id, user_id):
            return True

        # Check if project manager
        pm = db.scalar(
            select(ProjectMember).where(
                and_(
                    ProjectMember.project_id == project.id,
                    ProjectMember.user_id == user_id,
                    ProjectMember.role == ProjectRole.MANAGER,
                )
            )
        )
        return pm is not None

    @staticmethod
    def _validate_status_transition(
        db: Session,
        project: Project,
        new_status: ProjectStatus,
        cancellation_reason: Optional[str] = None,
    ) -> None:
        """
        Validate project status transitions.
        
        Ref: Module 3 - Feature 2.2 - AC 2
        """
        current = project.status

        # Define valid transitions
        valid_transitions = {
            ProjectStatus.NOT_STARTED: [ProjectStatus.IN_PROGRESS, ProjectStatus.CANCELLED],
            ProjectStatus.IN_PROGRESS: [ProjectStatus.IN_REVIEW, ProjectStatus.CANCELLED, ProjectStatus.DONE],
            ProjectStatus.IN_REVIEW: [ProjectStatus.DONE, ProjectStatus.IN_PROGRESS, ProjectStatus.CANCELLED],
            ProjectStatus.DONE: [],  # Terminal state (unless re-opened by admin)
            ProjectStatus.CANCELLED: [],  # Terminal state
        }

        if new_status not in valid_transitions.get(current, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from {current} to {new_status}"
            )

        # Special validations
        if new_status == ProjectStatus.CANCELLED and not cancellation_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cancellation reason is required when cancelling a project"
            )

        if new_status == ProjectStatus.DONE:
            # TODO: Check if all tasks are completed (Definition of Done)
            pass


class ProjectMemberService:
    """Service for project member management"""

    @staticmethod
    def add_member(
        db: Session,
        project_id: uuid.UUID,
        member_data: ProjectMemberCreate,
        current_user_id: uuid.UUID,
    ) -> ProjectMember:
        """
        Add a member to project.
        
        Args:
            db: Database session
            project_id: Project UUID
            member_data: Member data
            current_user_id: Current user ID (must be PM)
            
        Returns:
            Created project member
            
        Ref: Module 3 - Feature 2.3 - AC 1
        """
        project = ProjectService.get_project(db, project_id, current_user_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        # Check permission
        if not ProjectService._can_manage_project(db, project, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Project Manager can add members"
            )

        # Check if user is workspace member
        workspace_member = db.scalar(
            select(WorkspaceMember).where(
                and_(
                    WorkspaceMember.workspace_id == project.workspace_id,
                    WorkspaceMember.user_id == member_data.user_id,
                    WorkspaceMember.is_active == True,
                )
            )
        )

        if not workspace_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be a workspace member first"
            )

        # Check if already a member
        existing = db.scalar(
            select(ProjectMember).where(
                and_(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == member_data.user_id,
                )
            )
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a project member"
            )

        # Add member
        member = ProjectMember(
            project_id=project_id,
            user_id=member_data.user_id,
            role=member_data.role,
            joined_at=datetime.utcnow(),
        )

        db.add(member)
        db.commit()
        db.refresh(member)
        
        # TODO: Send notification to added user
        
        return member

    @staticmethod
    def update_member_role(
        db: Session,
        project_id: uuid.UUID,
        member_id: uuid.UUID,
        role_data: ProjectMemberUpdate,
        current_user_id: uuid.UUID,
    ) -> ProjectMember:
        """Update project member role"""
        project = ProjectService.get_project(db, project_id, current_user_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        if not ProjectService._can_manage_project(db, project, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Project Manager can update member roles"
            )

        member = db.scalar(
            select(ProjectMember).where(
                and_(
                    ProjectMember.id == member_id,
                    ProjectMember.project_id == project_id,
                )
            )
        )

        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project member not found"
            )

        member.role = role_data.role
        member.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def remove_member(
        db: Session,
        project_id: uuid.UUID,
        member_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> None:
        """Remove a member from project"""
        project = ProjectService.get_project(db, project_id, current_user_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        if not ProjectService._can_manage_project(db, project, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Project Manager can remove members"
            )

        member = db.scalar(
            select(ProjectMember).where(
                and_(
                    ProjectMember.id == member_id,
                    ProjectMember.project_id == project_id,
                )
            )
        )

        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project member not found"
            )

        # Cannot remove project owner
        if member.user_id == project.owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove project owner. Transfer ownership first."
            )

        db.delete(member)
        db.commit()

    @staticmethod
    def list_members(
        db: Session,
        project_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> List[ProjectMember]:
        """List all project members"""
        project = ProjectService.get_project(db, project_id, current_user_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        members = db.scalars(
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .order_by(ProjectMember.joined_at)
        ).all()

        return list(members)


class ProjectTemplateService:
    """Service for project template management"""

    @staticmethod
    def create_template(
        db: Session,
        template_data: ProjectTemplateCreate,
        creator_id: uuid.UUID,
    ) -> ProjectTemplate:
        """
        Create a project template.
        
        Ref: Module 3 - Feature 2.6
        """
        # Check if user can create global template (must be admin)
        if template_data.is_global:
            # TODO: Check if user is system admin
            pass

        template = ProjectTemplate(
            workspace_id=template_data.workspace_id,
            name=template_data.name,
            description=template_data.description,
            config=template_data.config,
            is_global=template_data.is_global,
            created_by=creator_id,
        )

        db.add(template)
        db.commit()
        db.refresh(template)
        return template

    @staticmethod
    def list_templates(
        db: Session,
        workspace_id: uuid.UUID,
        include_global: bool = True,
    ) -> List[ProjectTemplate]:
        """List available templates for a workspace"""
        conditions = [ProjectTemplate.workspace_id == workspace_id]
        
        if include_global:
            conditions.append(ProjectTemplate.is_global == True)

        templates = db.scalars(
            select(ProjectTemplate)
            .where(or_(*conditions))
            .order_by(ProjectTemplate.created_at.desc())
        ).all()

        return list(templates)


class ProjectChangeRequestService:
    """Service for change request management in STRICT governance mode"""

    @staticmethod
    def create_change_request(
        db: Session,
        cr_data: ChangeRequestCreate,
        creator_id: uuid.UUID,
    ) -> ProjectChangeRequest:
        """
        Create a change request.
        
        Ref: Module 3 - Feature 2.11 - AC 1
        """
        project = ProjectService.get_project(db, cr_data.project_id, creator_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        # Check if project is in STRICT mode
        if project.governance_mode != ProjectGovernanceMode.STRICT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Change requests are only available in STRICT governance mode"
            )

        cr = ProjectChangeRequest(
            project_id=cr_data.project_id,
            title=cr_data.title,
            description=cr_data.description,
            type=cr_data.type,
            status=ChangeRequestStatus.PENDING,
            impact_assessment=cr_data.impact_assessment,
            created_by=creator_id,
        )

        db.add(cr)
        db.commit()
        db.refresh(cr)
        return cr

    @staticmethod
    def approve_change_request(
        db: Session,
        cr_id: uuid.UUID,
        approval_data: ChangeRequestApprove,
        approver_id: uuid.UUID,
    ) -> ProjectChangeRequest:
        """
        Approve or reject a change request.
        
        Ref: Module 3 - Feature 2.11 - AC 2
        """
        cr = db.scalar(
            select(ProjectChangeRequest).where(ProjectChangeRequest.id == cr_id)
        )

        if not cr:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Change request not found"
            )

        project = ProjectService.get_project(db, cr.project_id, approver_id)
        
        # Check if user has approval rights (workspace admin or steering committee)
        if not ProjectService._is_workspace_admin(db, project.workspace_id, approver_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Workspace Admin can approve change requests"
            )

        cr.status = approval_data.status
        cr.approved_by = approver_id
        cr.approved_at = datetime.utcnow()
        cr.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(cr)
        
        # TODO: If approved, unlock constraints and notify PM
        
        return cr
