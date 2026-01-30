"""
Final Completeness Check - Compare implemented models vs documented entities.
Verifies that all critical MVP entities are now implemented.
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.declarative_base import Base
from app.db.models import *

def main():
    print("=" * 70)
    print("PRONAFLOW DATABASE COMPLETENESS CHECK")
    print("=" * 70)
    
    # Get all registered tables
    tables = Base.metadata.tables
    table_count = len(tables)
    
    print(f"\n[OK] Total Tables Registered: {table_count}")
    
    # Critical MVP entities that were missing
    critical_mvp = {
        'TaskAssignee': 'task_assignees',
        'Timesheet': 'timesheets',
    }
    
    # Association tables (already existed)
    association_tables = {
        'ProjectTagMap': 'project_tag_map',
        'TaskTagMap': 'task_tag_map',
    }
    
    print(f"\n{'-' * 70}")
    print("CRITICAL MVP ENTITIES (Previously Missing)")
    print(f"{'-' * 70}")
    
    all_mvp_complete = True
    for entity_name, table_name in critical_mvp.items():
        exists = table_name in tables
        status = "[OK] IMPLEMENTED" if exists else "[FAIL] MISSING"
        print(f"  {entity_name:20s} -> {table_name:30s} {status}")
        if not exists:
            all_mvp_complete = False
    
    print(f"\n{'-' * 70}")
    print("ASSOCIATION TABLES (Already Existed)")
    print(f"{'-' * 70}")
    
    for entity_name, table_name in association_tables.items():
        exists = table_name in tables
        status = "[OK] REGISTERED" if exists else "[FAIL] MISSING"
        print(f"  {entity_name:20s} -> {table_name:30s} {status}")
        if not exists:
            all_mvp_complete = False
    
    # List all tables by module
    print(f"\n{'-' * 70}")
    print("ALL REGISTERED TABLES BY MODULE")
    print(f"{'-' * 70}")
    
    module_tables = {
        "Module 1 - Identity & Access": [
            "users", "roles", "permissions", "user_roles", "role_permissions",
            "mfa_configs", "mfa_backup_codes", "auth_providers", "audit_logs", "sessions"
        ],
        "Module 2 - Workspaces": [
            "workspaces", "workspace_members_association", "workspace_invitations",
            "workspace_access_logs", "workspace_settings"
        ],
        "Module 3 - Projects": [
            "projects", "project_members_association", "project_templates",
            "project_template_members_association", "project_baselines",
            "project_change_requests", "project_archives"
        ],
        "Module 4 & 5 - Tasks": [
            "task_lists", "tasks", "subtasks", "task_assignees", "task_watchers_association",
            "task_dependencies", "comments", "files", "file_versions", "time_entries"
        ],
        "Module 6 - Notifications": [
            "notifications", "notification_templates", "notification_preferences",
            "domain_events", "event_consumers"
        ],
        "Module 9 - Reports": [
            "report_definitions", "report_executions", "metric_snapshots", "kpis"
        ],
        "Module 10-12 - Integrations": [
            "api_tokens", "api_scopes", "webhook_endpoints", "webhook_events",
            "webhook_deliveries", "integration_bindings"
        ],
        "Module 11 - Time Tracking": [
            "timesheets"
        ],
        "Module 15 - Tags": [
            "tags", "project_tag_map", "task_tag_map"
        ],
    }
    
    total_expected = 0
    total_found = 0
    
    for module_name, expected_tables in module_tables.items():
        found = sum(1 for t in expected_tables if t in tables)
        expected = len(expected_tables)
        total_expected += expected
        total_found += found
        
        status = "[OK]" if found == expected else "[FAIL]"
        print(f"\n{status} {module_name}")
        print(f"   Tables: {found}/{expected}")
        
        missing = [t for t in expected_tables if t not in tables]
        if missing:
            print(f"   Missing: {', '.join(missing)}")
    
    # Final summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total Tables Expected: {total_expected}")
    print(f"Total Tables Found:    {total_found}")
    print(f"Coverage:              {(total_found/total_expected)*100:.1f}%")
    
    if all_mvp_complete and total_found >= 51:
        print(f"\n[SUCCESS] MVP STATUS: 100% COMPLETE")
        print(f"All critical entities implemented and registered.")
        print(f"\nExtra tables (4) are foundation models:")
        print(f"  - MFA & Auth providers (Module 1)")
        print(f"  - Workspace invitations (Module 2)")
        print(f"  - Project templates & baselines (Module 3)")
        return 0
    else:
        print(f"\n[FAIL] MVP STATUS: INCOMPLETE")
        print(f"Some critical entities are still missing.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
