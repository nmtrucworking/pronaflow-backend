"""
Seed script for initial roles and permissions.
Creates RBAC roles and permissions required for Module 1.

Usage:
    python scripts/seed_roles_permissions.py
"""
import sys
import uuid
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.users import Role, Permission, role_permissions
from app.db.declarative_base import Base, engine


def seed_roles_and_permissions():
    """Seed initial roles and permissions"""
    
    print("🌱 Seeding Roles and Permissions...\n")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Define roles
        roles_data = [
            {"role_name": "OWNER", "hierarchy_level": 1},
            {"role_name": "ADMIN", "hierarchy_level": 2},
            {"role_name": "MEMBER", "hierarchy_level": 3},
            {"role_name": "GUEST", "hierarchy_level": 4},
        ]
        
        # Define permissions
        permissions_data = [
            {"code": "workspace:create", "description": "Create new workspace"},
            {"code": "workspace:delete", "description": "Delete workspace"},
            {"code": "workspace:manage", "description": "Manage workspace settings"},
            {"code": "workspace:invite", "description": "Invite members to workspace"},
            {"code": "project:create", "description": "Create new project"},
            {"code": "project:delete", "description": "Delete project"},
            {"code": "project:manage", "description": "Manage project settings"},
            {"code": "task:create", "description": "Create tasks"},
            {"code": "task:edit", "description": "Edit tasks"},
            {"code": "task:delete", "description": "Delete tasks"},
            {"code": "task:view", "description": "View tasks"},
            {"code": "comment:create", "description": "Create comments"},
            {"code": "comment:edit", "description": "Edit own comments"},
            {"code": "comment:delete", "description": "Delete comments"},
        ]
        
        # Create roles
        print("📋 Creating roles...")
        roles = {}
        for role_data in roles_data:
            existing_role = db.query(Role).filter(
                Role.role_name == role_data["role_name"]
            ).first()
            
            if existing_role:
                print(f"   ℹ️  Role '{role_data['role_name']}' already exists")
                roles[role_data["role_name"]] = existing_role
            else:
                role = Role(**role_data)
                db.add(role)
                roles[role_data["role_name"]] = role
                print(f"   ✅ Created role: {role_data['role_name']}")
        
        db.commit()
        
        # Create permissions
        print("\n🔐 Creating permissions...")
        permissions = {}
        for perm_data in permissions_data:
            existing_perm = db.query(Permission).filter(
                Permission.code == perm_data["code"]
            ).first()
            
            if existing_perm:
                print(f"   ℹ️  Permission '{perm_data['code']}' already exists")
                permissions[perm_data["code"]] = existing_perm
            else:
                perm = Permission(**perm_data)
                db.add(perm)
                permissions[perm_data["code"]] = perm
                print(f"   ✅ Created permission: {perm_data['code']}")
        
        db.commit()
        
        # Assign permissions to roles
        print("\n🔗 Assigning permissions to roles...\n")
        
        # OWNER -All permissions
        owner_perms = permissions.keys()
        for perm_code in owner_perms:
            if permissions[perm_code] not in roles["OWNER"].permissions:
                roles["OWNER"].permissions.append(permissions[perm_code])
        print(f"   ✅ OWNER: {len(owner_perms)} permissions")
        
        # ADMIN - All except workspace delete
        admin_perms = [p for p in permissions.keys() if p != "workspace:delete"]
        for perm_code in admin_perms:
            if permissions[perm_code] not in roles["ADMIN"].permissions:
                roles["ADMIN"].permissions.append(permissions[perm_code])
        print(f"   ✅ ADMIN: {len(admin_perms)} permissions")
        
        # MEMBER - Project and task management
        member_perms = [
            "project:create", "task:create", "task:edit", "task:view",
            "comment:create", "comment:edit"
        ]
        for perm_code in member_perms:
            if perm_code in permissions and permissions[perm_code] not in roles["MEMBER"].permissions:
                roles["MEMBER"].permissions.append(permissions[perm_code])
        print(f"   ✅ MEMBER: {len(member_perms)} permissions")
        
        # GUEST - Read-only
        guest_perms = ["task:view"]
        for perm_code in guest_perms:
            if perm_code in permissions and permissions[perm_code] not in roles["GUEST"].permissions:
                roles["GUEST"].permissions.append(permissions[perm_code])
        print(f"   ✅ GUEST: {len(guest_perms)} permissions")
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("✅ Roles and permissions seeded successfully!")
        print("=" * 60)
        
        # Print summary
        print("\n📊 Summary:")
        print(f"   Roles: {len(roles)}")
        print(f"   Permissions: {len(permissions)}")
        print("\n🎯 Role Hierarchy:")
        for role_data in sorted(roles_data, key=lambda x: x["hierarchy_level"]):
            role = roles[role_data["role_name"]]
            perm_count = len(role.permissions)
            print(f"   {role_data['hierarchy_level']}. {role_data['role_name']:<10} - {perm_count} permissions")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_roles_and_permissions()
