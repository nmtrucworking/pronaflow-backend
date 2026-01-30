"""
Example usage of the Workspace module.
Demonstrates common patterns and workflows.
"""

# ============================================================================
# Example 1: Create a Workspace (Workspace Creation - AC 1)
# ============================================================================

from sqlalchemy.orm import Session
from app.services.workspace import WorkspaceService
from app.schemas.workspace import WorkspaceCreate
import uuid

def example_create_workspace(db: Session, user_id: uuid.UUID):
    """Create a new workspace with the current user as owner."""
    
    workspace_data = WorkspaceCreate(
        name="Engineering Team",
        description="Main workspace for engineering department"
    )
    
    # Service automatically:
    # 1. Creates workspace record
    # 2. Assigns user as OWNER
    # 3. Creates default settings
    # 4. Logs access/context switch
    workspace = WorkspaceService.create_workspace(
        db=db,
        workspace_data=workspace_data,
        owner_id=user_id
    )
    
    print(f"✅ Created workspace: {workspace.name} ({workspace.id})")
    print(f"   Owner: {workspace.owner_id}")
    print(f"   Status: {workspace.status}")
    
    return workspace


# ============================================================================
# Example 2: List User's Workspaces
# ============================================================================

def example_list_workspaces(db: Session, user_id: uuid.UUID):
    """Get all workspaces for a user."""
    
    workspaces, total = WorkspaceService.list_user_workspaces(
        db=db,
        user_id=user_id,
        skip=0,
        limit=10
    )
    
    print(f"\n📋 Found {total} workspaces for user {user_id}:")
    for ws in workspaces:
        print(f"   • {ws.name} (ID: {ws.id}, Owner: {ws.owner_id})")
    
    return workspaces, total


# ============================================================================
# Example 3: Add Members to Workspace
# ============================================================================

from app.services.workspace import WorkspaceMemberService
from app.schemas.workspace import WorkspaceMemberCreate
from app.db.enums import WorkspaceRole

def example_add_member(db: Session, workspace_id: uuid.UUID, new_user_id: uuid.UUID):
    """Add a user to workspace with MEMBER role."""
    
    member_data = WorkspaceMemberCreate(
        user_id=new_user_id,
        role=WorkspaceRole.MEMBER
    )
    
    member = WorkspaceMemberService.add_member(
        db=db,
        workspace_id=workspace_id,
        member_data=member_data
    )
    
    if member:
        print(f"\n✅ Added user {new_user_id} to workspace")
        print(f"   Role: {member.role}")
        print(f"   Active: {member.is_active}")
        print(f"   Joined: {member.joined_at}")
    else:
        print(f"❌ Failed to add user (user may not exist)")
    
    return member


# ============================================================================
# Example 4: List Workspace Members
# ============================================================================

def example_list_members(db: Session, workspace_id: uuid.UUID):
    """List all members in a workspace."""
    
    members, total = WorkspaceMemberService.list_members(
        db=db,
        workspace_id=workspace_id,
        skip=0,
        limit=50
    )
    
    print(f"\n👥 Workspace has {total} members:")
    for member in members:
        print(f"   • User {member.user_id}")
        print(f"     Role: {member.role.value}")
        print(f"     Active: {member.is_active}")
        print(f"     Joined: {member.joined_at}")
    
    return members, total


# ============================================================================
# Example 5: Update Member Role
# ============================================================================

from app.schemas.workspace import WorkspaceMemberUpdate

def example_update_member_role(
    db: Session,
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
    new_role: WorkspaceRole
):
    """Promote a member to admin role."""
    
    update_data = WorkspaceMemberUpdate(role=new_role)
    
    member = WorkspaceMemberService.update_member(
        db=db,
        workspace_id=workspace_id,
        user_id=user_id,
        update_data=update_data
    )
    
    if member:
        print(f"\n✅ Updated member role")
        print(f"   User: {user_id}")
        print(f"   New role: {member.role.value}")
    else:
        print(f"❌ Member not found")
    
    return member


# ============================================================================
# Example 6: Send Workspace Invitation (Magic Link)
# ============================================================================

from app.services.workspace import WorkspaceInvitationService
from app.schemas.workspace import WorkspaceInvitationCreate

def example_send_invitation(
    db: Session,
    workspace_id: uuid.UUID,
    inviter_user_id: uuid.UUID,
    target_email: str
):
    """Send invitation to join workspace via email."""
    
    invitation_data = WorkspaceInvitationCreate(
        email=target_email,
        invited_role=WorkspaceRole.MEMBER
    )
    
    invitation = WorkspaceInvitationService.create_invitation(
        db=db,
        workspace_id=workspace_id,
        invited_by=inviter_user_id,
        invitation_data=invitation_data,
        expires_in_hours=48  # Expires in 48 hours
    )
    
    print(f"\n📧 Sent invitation:")
    print(f"   To: {invitation.email}")
    print(f"   Role: {invitation.invited_role.value}")
    print(f"   Token Hash: {invitation.token_hash}")
    print(f"   Expires: {invitation.expires_at}")
    print(f"   Status: Pending (not accepted)")
    
    # TODO: Send actual email with magic link containing the token
    # email_service.send_invitation_email(
    #     to_email=invitation.email,
    #     workspace_name=workspace.name,
    #     magic_link=f"https://app.example.com/join/{invitation.token}"
    # )
    
    return invitation


# ============================================================================
# Example 7: List Pending Invitations
# ============================================================================

def example_list_pending_invitations(db: Session, workspace_id: uuid.UUID):
    """List all pending (not yet accepted) invitations."""
    
    invitations, total = WorkspaceInvitationService.list_pending_invitations(
        db=db,
        workspace_id=workspace_id,
        skip=0,
        limit=50
    )
    
    print(f"\n📧 Found {total} pending invitations:")
    for inv in invitations:
        print(f"   • {inv.email}")
        print(f"     Role: {inv.invited_role.value}")
        print(f"     Expires: {inv.expires_at}")
        print(f"     Invited by: {inv.invited_by}")
    
    return invitations, total


# ============================================================================
# Example 8: Accept Invitation
# ============================================================================

def example_accept_invitation(
    db: Session,
    invitation_id: uuid.UUID,
    accepting_user_id: uuid.UUID
):
    """User accepts workspace invitation and becomes member."""
    
    member = WorkspaceInvitationService.accept_invitation(
        db=db,
        invitation_id=invitation_id,
        user_id=accepting_user_id
    )
    
    if member:
        print(f"\n✅ Invitation accepted!")
        print(f"   User: {accepting_user_id}")
        print(f"   Workspace: {member.workspace_id}")
        print(f"   Role: {member.role.value}")
    else:
        print(f"❌ Could not accept (invalid, expired, or already accepted)")
    
    return member


# ============================================================================
# Example 9: Log Workspace Access (Context Switch)
# ============================================================================

from app.services.workspace import WorkspaceAccessLogService

def example_log_access(
    db: Session,
    workspace_id: uuid.UUID,
    user_id: uuid.UUID
):
    """Log user's access to workspace for audit trail."""
    
    log = WorkspaceAccessLogService.log_access(
        db=db,
        workspace_id=workspace_id,
        user_id=user_id
    )
    
    print(f"\n📝 Logged workspace access:")
    print(f"   User: {user_id}")
    print(f"   Workspace: {workspace_id}")
    print(f"   Time: {log.created_at}")
    
    return log


# ============================================================================
# Example 10: Get Access History (Audit Log)
# ============================================================================

def example_get_access_history(
    db: Session,
    workspace_id: uuid.UUID,
    filter_user_id: uuid.UUID | None = None
):
    """Retrieve workspace access history for audit purposes."""
    
    logs, total = WorkspaceAccessLogService.get_access_history(
        db=db,
        workspace_id=workspace_id,
        user_id=filter_user_id,  # Optional: filter by user
        skip=0,
        limit=50
    )
    
    print(f"\n📊 Access history ({total} total):")
    for log in logs:
        print(f"   • User {log.user_id} accessed at {log.created_at}")
    
    return logs, total


# ============================================================================
# Example 11: Update Workspace Settings
# ============================================================================

from app.services.workspace import WorkspaceSettingService
from app.schemas.workspace import WorkspaceSettingUpdate

def example_update_workspace_settings(
    db: Session,
    workspace_id: uuid.UUID
):
    """Update workspace configuration."""
    
    settings_data = WorkspaceSettingUpdate(
        timezone="Asia/Ho_Chi_Minh",
        work_days="Mon,Tue,Wed,Thu,Fri",
        work_hours='{"start": "09:00", "end": "18:00"}',
        logo_url="https://example.com/logo.png"
    )
    
    settings = WorkspaceSettingService.update_settings(
        db=db,
        workspace_id=workspace_id,
        update_data=settings_data
    )
    
    if settings:
        print(f"\n⚙️ Updated workspace settings:")
        print(f"   Timezone: {settings.timezone}")
        print(f"   Work days: {settings.work_days}")
        print(f"   Work hours: {settings.work_hours}")
        print(f"   Logo URL: {settings.logo_url}")
    else:
        print(f"❌ Settings not found")
    
    return settings


# ============================================================================
# Example 12: Remove Member
# ============================================================================

def example_remove_member(
    db: Session,
    workspace_id: uuid.UUID,
    user_id: uuid.UUID
):
    """Remove member from workspace (soft removal)."""
    
    success = WorkspaceMemberService.remove_member(
        db=db,
        workspace_id=workspace_id,
        user_id=user_id
    )
    
    if success:
        print(f"\n❌ Removed user {user_id} from workspace")
    else:
        print(f"❌ Member not found")
    
    return success


# ============================================================================
# Example 13: Cancel Invitation
# ============================================================================

def example_cancel_invitation(
    db: Session,
    invitation_id: uuid.UUID
):
    """Cancel a pending invitation."""
    
    success = WorkspaceInvitationService.cancel_invitation(
        db=db,
        invitation_id=invitation_id
    )
    
    if success:
        print(f"\n✅ Invitation {invitation_id} cancelled")
    else:
        print(f"❌ Invitation not found or already accepted")
    
    return success


# ============================================================================
# Example 14: Delete Workspace (Soft Delete)
# ============================================================================

def example_delete_workspace(
    db: Session,
    workspace_id: uuid.UUID
):
    """Soft delete a workspace."""
    
    success = WorkspaceService.delete_workspace(
        db=db,
        workspace_id=workspace_id
    )
    
    if success:
        print(f"\n🗑️ Workspace {workspace_id} deleted")
    else:
        print(f"❌ Workspace not found")
    
    return success


# ============================================================================
# Example 15: Complete Workflow - Setup New Team
# ============================================================================

def example_complete_workflow(db: Session, owner_user_id: uuid.UUID):
    """Complete workflow: Create workspace, add members, configure settings."""
    
    print("\n" + "="*60)
    print("COMPLETE WORKFLOW EXAMPLE: Setting up new team")
    print("="*60)
    
    # Step 1: Create workspace
    print("\n[1/5] Creating workspace...")
    workspace_data = WorkspaceCreate(
        name="Design Team 2024",
        description="Design team workspace for 2024 projects"
    )
    workspace = WorkspaceService.create_workspace(db, workspace_data, owner_user_id)
    print(f"✅ Workspace created: {workspace.name}")
    
    # Step 2: Configure settings
    print("\n[2/5] Configuring workspace settings...")
    settings_update = WorkspaceSettingUpdate(
        timezone="UTC",
        work_days="Mon,Tue,Wed,Thu,Fri",
        work_hours='{"start": "09:00", "end": "17:00"}'
    )
    WorkspaceSettingService.update_settings(db, workspace.id, settings_update)
    print("✅ Settings configured")
    
    # Step 3: Add team members directly
    print("\n[3/5] Adding team members...")
    team_members = [
        uuid.uuid4(),  # Designer 1
        uuid.uuid4(),  # Designer 2
    ]
    for team_member_id in team_members:
        member_data = WorkspaceMemberCreate(
            user_id=team_member_id,
            role=WorkspaceRole.MEMBER
        )
        WorkspaceMemberService.add_member(db, workspace.id, member_data)
        print(f"✅ Added member {team_member_id}")
    
    # Step 4: Send invitations to stakeholders
    print("\n[4/5] Sending invitations to stakeholders...")
    stakeholders = [
        "manager@example.com",
        "stakeholder@example.com"
    ]
    for email in stakeholders:
        invitation_data = WorkspaceInvitationCreate(
            email=email,
            invited_role=WorkspaceRole.VIEWER
        )
        WorkspaceInvitationService.create_invitation(
            db, workspace.id, owner_user_id, invitation_data
        )
        print(f"✅ Invitation sent to {email}")
    
    # Step 5: Verify setup
    print("\n[5/5] Verifying setup...")
    members, member_count = WorkspaceMemberService.list_members(db, workspace.id)
    invitations, invitation_count = WorkspaceInvitationService.list_pending_invitations(
        db, workspace.id
    )
    print(f"✅ Setup complete:")
    print(f"   - Workspace: {workspace.name}")
    print(f"   - Members: {member_count}")
    print(f"   - Pending invitations: {invitation_count}")
    
    return workspace


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    """
    Run examples (requires database connection)
    
    Usage:
        python examples.py
    """
    print("Workspace Module Examples")
    print("=" * 60)
    print("\nThese are example functions demonstrating the workspace module.")
    print("To run, uncomment desired examples and provide a database session.")
    print("\nExample functions available:")
    print("  - example_create_workspace()")
    print("  - example_list_workspaces()")
    print("  - example_add_member()")
    print("  - example_list_members()")
    print("  - example_send_invitation()")
    print("  - example_accept_invitation()")
    print("  - example_log_access()")
    print("  - example_complete_workflow()")
    print("\nRefer to WORKSPACE_QUICK_REFERENCE.md for detailed API documentation.")
