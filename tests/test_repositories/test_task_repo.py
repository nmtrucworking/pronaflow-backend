"""
Unit tests for Task Repository (Module 4)
"""
import pytest
from datetime import datetime, timedelta
from app.db.repositories.task_repo import TaskRepository, TaskListRepository
from app.db.models.tasks import Task, TaskList


@pytest.mark.unit
class TestTaskRepository:
    """Test suite for TaskRepository."""
    
    @pytest.fixture
    def setup_dependencies(self, db_session):
        """Setup user, workspace, and project for tasks."""
        from app.db.repositories.user_repo import UserRepository
        from app.db.repositories.workspace_repo import WorkspaceRepository
        from app.db.repositories.project_repo import ProjectRepository
        
        # Create user
        user_repo = UserRepository(db_session)
        user = user_repo.create(
            email="taskuser@example.com",
            full_name="Task User",
            password_hash="hashed"
        )
        
        # Create workspace
        workspace_repo = WorkspaceRepository(db_session)
        workspace = workspace_repo.create(
            name="Task Workspace",
            slug="task-workspace",
            owner_id=user.id
        )
        
        # Create project
        project_repo = ProjectRepository(db_session)
        project = project_repo.create(
            name="Task Project",
            key="TASK",
            workspace_id=workspace.id,
            created_by=user.id
        )
        
        db_session.commit()
        
        return {
            "user": user,
            "workspace": workspace,
            "project": project
        }
    
    def test_create_task(self, db_session, setup_dependencies):
        """Test creating a new task."""
        deps = setup_dependencies
        repo = TaskRepository(db_session)
        
        task = repo.create(
            title="New Task",
            description="Task description",
            status="TODO",
            priority="HIGH",
            project_id=deps["project"].id,
            created_by=deps["user"].id
        )
        
        assert task.id is not None
        assert task.title == "New Task"
        assert task.status == "TODO"
        assert task.priority == "HIGH"
        assert task.project_id == deps["project"].id
    
    def test_get_project_tasks(self, db_session, setup_dependencies):
        """Test retrieving all tasks for a project."""
        deps = setup_dependencies
        repo = TaskRepository(db_session)
        
        # Create multiple tasks
        for i in range(3):
            repo.create(
                title=f"Task {i}",
                status="TODO",
                project_id=deps["project"].id,
                created_by=deps["user"].id
            )
        db_session.commit()
        
        # Get project tasks
        tasks = repo.get_project_tasks(deps["project"].id)
        
        assert len(tasks) >= 3
    
    def test_update_task_status(self, db_session, setup_dependencies):
        """Test updating task status."""
        deps = setup_dependencies
        repo = TaskRepository(db_session)
        
        task = repo.create(
            title="Status Test",
            status="TODO",
            project_id=deps["project"].id,
            created_by=deps["user"].id
        )
        db_session.commit()
        
        # Update status
        updated = repo.update(task.id, status="IN_PROGRESS")
        db_session.commit()
        
        assert updated.status == "IN_PROGRESS"
    
    def test_get_tasks_by_assignee(self, db_session, setup_dependencies):
        """Test retrieving tasks assigned to a user."""
        deps = setup_dependencies
        repo = TaskRepository(db_session)
        
        # Create task with assignee
        task = repo.create(
            title="Assigned Task",
            status="TODO",
            project_id=deps["project"].id,
            created_by=deps["user"].id,
            assignee_id=deps["user"].id
        )
        db_session.commit()
        
        # Get assigned tasks
        tasks = repo.get_by_assignee(deps["user"].id)
        
        assert len(tasks) >= 1
        assert any(t.id == task.id for t in tasks)
    
    def test_get_overdue_tasks(self, db_session, setup_dependencies):
        """Test retrieving overdue tasks."""
        deps = setup_dependencies
        repo = TaskRepository(db_session)
        
        # Create overdue task
        yesterday = datetime.utcnow() - timedelta(days=1)
        task = repo.create(
            title="Overdue Task",
            status="IN_PROGRESS",
            due_date=yesterday,
            project_id=deps["project"].id,
            created_by=deps["user"].id
        )
        db_session.commit()
        
        # Get overdue tasks
        overdue = repo.get_overdue_tasks(deps["project"].id)
        
        assert len(overdue) >= 1
        assert any(t.id == task.id for t in overdue)


@pytest.mark.unit
class TestTaskListRepository:
    """Test suite for TaskListRepository."""
    
    @pytest.fixture
    def setup_project(self, db_session):
        """Setup project for task lists."""
        from app.db.repositories.user_repo import UserRepository
        from app.db.repositories.workspace_repo import WorkspaceRepository
        from app.db.repositories.project_repo import ProjectRepository
        
        user_repo = UserRepository(db_session)
        user = user_repo.create(
            email="listuser@example.com",
            full_name="List User",
            password_hash="hashed"
        )
        
        workspace_repo = WorkspaceRepository(db_session)
        workspace = workspace_repo.create(
            name="List Workspace",
            slug="list-workspace",
            owner_id=user.id
        )
        
        project_repo = ProjectRepository(db_session)
        project = project_repo.create(
            name="List Project",
            key="LIST",
            workspace_id=workspace.id,
            created_by=user.id
        )
        
        db_session.commit()
        return {"user": user, "project": project}
    
    def test_create_task_list(self, db_session, setup_project):
        """Test creating a task list."""
        deps = setup_project
        repo = TaskListRepository(db_session)
        
        task_list = repo.create(
            name="To Do",
            project_id=deps["project"].id,
            position=0
        )
        
        assert task_list.id is not None
        assert task_list.name == "To Do"
        assert task_list.position == 0
    
    def test_get_project_lists(self, db_session, setup_project):
        """Test retrieving all lists for a project."""
        deps = setup_project
        repo = TaskListRepository(db_session)
        
        # Create multiple lists
        lists = ["To Do", "In Progress", "Done"]
        for i, name in enumerate(lists):
            repo.create(
                name=name,
                project_id=deps["project"].id,
                position=i
            )
        db_session.commit()
        
        # Get project lists
        project_lists = repo.get_project_lists(deps["project"].id)
        
        assert len(project_lists) >= 3
        # Should be ordered by position
        assert project_lists[0].name == "To Do"
