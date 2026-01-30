#!/usr/bin/env python3
"""
Comprehensive Entity Analysis for PronaFlow
Analyzes all 154 entities from documentation and backend implementation
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict

# ============= ENTITY DEFINITIONS =============

@dataclass
class EntityField:
    name: str
    field_type: str
    key_type: str = ""  # PK, FK, etc
    constraints: str = ""
    note: str = ""

@dataclass
class Entity:
    name: str
    module: str = ""
    fields: List[EntityField] = field(default_factory=list)
    description: str = ""
    mvp_category: str = "unknown"  # must-have, advanced, admin, etc
    is_implemented: bool = False
    implementation_file: str = ""
    
    @property
    def field_summary(self) -> str:
        """Generate brief field summary"""
        core_fields = [f.name for f in self.fields[:3]]
        return ", ".join(core_fields) + ("..." if len(self.fields) > 3 else "")

# ============= MVP CLASSIFICATION =============

MVP_MUST_HAVE = {
    # Core functionality - absolutely needed for MVP
    "User", "Role", "Permission", 
    "Workspace", "WorkspaceMember", 
    "Project", "ProjectMember",
    "Task", "TaskList", "Subtask",
    "Comment", "File", "FileVersion",
    "Tag", "TaskTagMap", "ProjectTagMap",
    "Notification", "NotificationPreference",
    "TimeEntry", "Timesheet",
    "AuditLog", "Session",
    "WebhookEndpoint", "WebhookEvent", "WebhookDelivery",
    "ApiToken", "ApiScope",
}

MVP_ADVANCED = {
    # Features nice to have but not critical
    "UserSettings", "UIViewPreference", "KeyboardShortcut",
    "ProjectTemplate", "TaskTemplate", "NoteTemplate",
    "TaskDependency", "TaskAssignee", "TaskWatcher",
    "UserRole", "RolePermission",
    "MFAConfig", "MFABackupCode",
    "OnboardingChecklist", "UserOnboardingStatus",
    "ProductTour", "FeatureBeacon",
    "Note", "NoteVersion", "PublicNoteLink",
    "ReportDefinition", "ReportExecution", "KPI",
    "IntegrationBinding",
}

MVP_ADMIN = {
    # Admin/Operations only
    "AdminUser", "AdminRole", "AdminPermission",
    "AdminAuditLog", "AdminUserRole", "AdminRolePermission",
    "AdminPermission", "AdminUser", "AdminRole",
    "SecurityIncident", "SystemConfig",
}

MVP_ADVANCED_EXTENDED = {
    # Advanced features - future phases
    "Article", "ArticleVersion", "ArticleTranslation",
    "Category", "SearchIndex",
    "Mention", "ConsentGrant",
    "MLModel", "ModelVersion", "ModelMetric",
    "InferenceRequest", "InferenceResult",
}

# ============= FILE READING =============

def read_entity_md(filepath: str) -> Tuple[str, str, List[EntityField]]:
    """Parse entity markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract module
        module_match = re.search(r'#\s*(?:Module|Phân hệ)\s+(\d+[^#\n]*)', content)
        module = module_match.group(1).strip() if module_match else "unknown"
        
        # Extract description
        desc_match = re.search(r'>(.+?)(?=#|$)', content)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # Extract fields from markdown table
        fields = []
        table_pattern = r'\|(.+?)\|(.+?)\|(.+?)\|'
        
        lines = content.split('\n')
        in_table = False
        for line in lines:
            if '|' in line and ('Field' in line or 'field' in line.lower()):
                in_table = True
                continue
            if in_table and '|' in line and line.strip().startswith('|'):
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 2 and parts[0] and not parts[0].startswith('---'):
                    field_name = parts[0].replace('(PK)', '').replace('(FK)', '').strip()
                    field_type = parts[1] if len(parts) > 1 else ""
                    key = "(PK)" if "(PK)" in parts[0] else "(FK)" if "(FK)" in parts[0] else ""
                    
                    fields.append(EntityField(
                        name=field_name,
                        field_type=field_type,
                        key_type=key
                    ))
        
        return module, description, fields
    except Exception as e:
        return "", "", []

# ============= IMPLEMENTATION DETECTION =============

def detect_implemented_entities(models_dir: str) -> Dict[str, str]:
    """Scan models directory to find implemented entities"""
    implemented = {}
    
    model_files = {
        'module_1.py': ['User', 'Role', 'Permission', 'MFAConfig', 'MFABackupCode', 'AuthProvider', 'AuditLog', 'Session'],
        'workspaces.py': ['Workspace', 'WorkspaceMember', 'WorkspaceInvitation', 'WorkspaceAccessLog', 'WorkspaceSetting'],
        'projects.py': ['Project'],
        'projects_extended.py': ['ProjectMember', 'ProjectTemplate', 'ProjectBaseline', 'ProjectChangeRequest', 'ProjectArchive'],
        'tasks.py': ['TaskList', 'Task', 'Subtask', 'TaskDependency', 'Comment', 'File', 'FileVersion', 'TimeEntry'],
        'tags.py': ['Tag'],
        'notifications.py': ['Notification', 'NotificationTemplate', 'NotificationPreference', 'DomainEvent', 'EventConsumer'],
        'reports.py': ['ReportDefinition', 'ReportExecution', 'MetricSnapshot', 'KPI'],
        'integrations.py': ['ApiToken', 'ApiScope', 'WebhookEndpoint', 'WebhookEvent', 'WebhookDelivery', 'IntegrationBinding'],
    }
    
    for filename, entities in model_files.items():
        for entity in entities:
            implemented[entity] = filename
    
    return implemented

# ============= MAIN ANALYSIS =============

def analyze_all_entities(entities_dir: str, models_dir: str) -> Dict[str, Entity]:
    """Analyze all 154 entities"""
    entities = {}
    implemented = detect_implemented_entities(models_dir)
    
    # Read all entity markdown files
    md_files = sorted(Path(entities_dir).glob('*.md'))
    
    for md_file in md_files:
        entity_name = md_file.stem
        module, description, fields = read_entity_md(str(md_file))
        
        # Classify by MVP priority
        if entity_name in MVP_MUST_HAVE:
            mvp_category = "must-have"
        elif entity_name in MVP_ADVANCED:
            mvp_category = "advanced"
        elif entity_name in MVP_ADMIN:
            mvp_category = "admin"
        elif entity_name in MVP_ADVANCED_EXTENDED:
            mvp_category = "extended"
        else:
            mvp_category = "other"
        
        entity = Entity(
            name=entity_name,
            module=module,
            fields=fields,
            description=description,
            mvp_category=mvp_category,
            is_implemented=entity_name in implemented,
            implementation_file=implemented.get(entity_name, "")
        )
        
        entities[entity_name] = entity
    
    return entities

# ============= REPORTING =============

def generate_report(entities: Dict[str, Entity]) -> str:
    """Generate comprehensive analysis report"""
    
    # Group by MVP category
    categories = defaultdict(list)
    for entity in entities.values():
        categories[entity.mvp_category].append(entity)
    
    # Sort within each category
    for cat in categories:
        categories[cat].sort(key=lambda e: e.name)
    
    report = []
    report.append("# PronaFlow Entity Analysis Report")
    report.append(f"**Total Entities: {len(entities)}**\n")
    
    # ========== MUST-HAVE CORE (MVP) ==========
    report.append("## 🔴 MUST-HAVE CORE (MVP) - CRITICAL\n")
    report.append("These entities are essential for MVP launch:\n")
    
    must_have = categories.get('must-have', [])
    for entity in must_have:
        status = "✓ DONE" if entity.is_implemented else "✗ MISSING"
        fields_info = f"{len(entity.fields)} fields" if entity.fields else "No fields"
        report.append(f"- **{entity.name}** [{status}] ({fields_info})")
        if entity.fields:
            field_names = [f.name for f in entity.fields[:5]]
            report.append(f"  Fields: {', '.join(field_names)}")
    
    report.append(f"\n**Summary: {len(must_have)} entities** | ")
    report.append(f"Implemented: {sum(1 for e in must_have if e.is_implemented)} | ")
    report.append(f"Missing: {sum(1 for e in must_have if not e.is_implemented)}\n")
    
    # ========== ADVANCED FEATURES ==========
    report.append("\n## 🟡 ADVANCED FEATURES - TIER 2\n")
    report.append("These enhance functionality but aren't essential for MVP:\n")
    
    advanced = categories.get('advanced', [])
    for entity in advanced:
        status = "✓ DONE" if entity.is_implemented else "✗ MISSING"
        fields_info = f"{len(entity.fields)} fields" if entity.fields else "No fields"
        report.append(f"- **{entity.name}** [{status}] ({fields_info})")
    
    report.append(f"\n**Summary: {len(advanced)} entities** | ")
    report.append(f"Implemented: {sum(1 for e in advanced if e.is_implemented)} | ")
    report.append(f"Missing: {sum(1 for e in advanced if not e.is_implemented)}\n")
    
    # ========== ADMIN ONLY ==========
    report.append("\n## 🔵 ADMIN & OPERATIONS ONLY\n")
    report.append("These are for system administration and don't impact user experience:\n")
    
    admin = categories.get('admin', [])
    for entity in admin:
        status = "✓ DONE" if entity.is_implemented else "✗ MISSING"
        fields_info = f"{len(entity.fields)} fields" if entity.fields else "No fields"
        report.append(f"- **{entity.name}** [{status}] ({fields_info})")
    
    report.append(f"\n**Summary: {len(admin)} entities** | ")
    report.append(f"Implemented: {sum(1 for e in admin if e.is_implemented)} | ")
    report.append(f"Missing: {sum(1 for e in admin if not e.is_implemented)}\n")
    
    # ========== EXTENDED/FUTURE ==========
    report.append("\n## 🟢 EXTENDED FEATURES - FUTURE PHASES\n")
    report.append("Advanced features for future releases:\n")
    
    extended = categories.get('extended', [])
    for entity in extended:
        status = "✓ DONE" if entity.is_implemented else "✗ MISSING"
        fields_info = f"{len(entity.fields)} fields" if entity.fields else "No fields"
        report.append(f"- **{entity.name}** [{status}] ({fields_info})")
    
    report.append(f"\n**Summary: {len(extended)} entities** | ")
    report.append(f"Implemented: {sum(1 for e in extended if e.is_implemented)} | ")
    report.append(f"Missing: {sum(1 for e in extended if not e.is_implemented)}\n")
    
    # ========== OTHER ==========
    other = categories.get('other', [])
    if other:
        report.append("\n## ⚪ OTHER / UNCLASSIFIED\n")
        for entity in other:
            status = "✓ DONE" if entity.is_implemented else "✗ MISSING"
            report.append(f"- **{entity.name}** [{status}]")
    
    # ========== IMPLEMENTATION STATUS ==========
    report.append("\n\n## 📊 IMPLEMENTATION STATUS\n")
    
    all_implemented = [e for e in entities.values() if e.is_implemented]
    all_missing = [e for e in entities.values() if not e.is_implemented]
    
    report.append(f"**Total Implemented: {len(all_implemented)}/{len(entities)}** ({len(all_implemented)*100//len(entities)}%)\n")
    
    report.append(f"**Implemented by Module:**\n")
    by_file = defaultdict(list)
    for entity in all_implemented:
        by_file[entity.implementation_file].append(entity.name)
    
    for filename in sorted(by_file.keys()):
        report.append(f"- `{filename}`: {', '.join(sorted(by_file[filename]))}\n")
    
    # ========== MISSING ENTITIES ==========
    report.append(f"\n## ❌ MISSING ENTITIES ({len(all_missing)} total)\n")
    
    # Priority: must-have > advanced > rest
    missing_must_have = [e for e in all_missing if e.mvp_category == 'must-have']
    missing_advanced = [e for e in all_missing if e.mvp_category == 'advanced']
    missing_other = [e for e in all_missing if e.mvp_category not in ['must-have', 'advanced']]
    
    if missing_must_have:
        report.append(f"\n### 🔴 CRITICAL TO IMPLEMENT NOW ({len(missing_must_have)})\n")
        for entity in sorted(missing_must_have, key=lambda e: e.name):
            report.append(f"- **{entity.name}** - Module {entity.module}\n")
    
    if missing_advanced:
        report.append(f"\n### 🟡 SHOULD IMPLEMENT SOON ({len(missing_advanced)})\n")
        for entity in sorted(missing_advanced, key=lambda e: e.name)[:20]:  # Show first 20
            report.append(f"- **{entity.name}** - Module {entity.module}\n")
        if len(missing_advanced) > 20:
            report.append(f"- ... and {len(missing_advanced) - 20} more\n")
    
    if missing_other:
        report.append(f"\n### 🔵 CAN IMPLEMENT LATER ({len(missing_other)})\n")
        report.append(f"- {len(missing_other)} other entities\n")
    
    # ========== STATISTICS ==========
    report.append("\n## 📈 STATISTICS\n")
    report.append(f"- Total Entities: {len(entities)}\n")
    report.append(f"- Must-Have: {len(must_have)} entities\n")
    report.append(f"- Advanced: {len(advanced)} entities\n")
    report.append(f"- Admin: {len(admin)} entities\n")
    report.append(f"- Extended: {len(extended)} entities\n")
    report.append(f"- Other: {len(other)} entities\n")
    report.append(f"- Implemented: {len(all_implemented)} ({len(all_implemented)*100//len(entities)}%)\n")
    report.append(f"- Missing: {len(all_missing)} ({len(all_missing)*100//len(entities)}%)\n")
    
    return "\n".join(report)

# ============= MAIN EXECUTION =============

if __name__ == "__main__":
    entities_dir = r'docs\docs - PronaFlow React&FastAPI\02-Architeture\Entities'
    models_dir = r'app\db\models'
    
    print("🔍 Analyzing all 154 entities...\n")
    
    # Analyze entities
    entities = analyze_all_entities(entities_dir, models_dir)
    
    # Generate and print report
    report = generate_report(entities)
    print(report)
    
    # Save to file
    with open('ENTITY_ANALYSIS_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n✅ Report saved to: ENTITY_ANALYSIS_REPORT.md")
