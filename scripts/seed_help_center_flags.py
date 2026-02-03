"""
Seed feature flags for Module 15 Help Center
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.admin import FeatureFlag
from datetime import datetime


def seed_help_center_feature_flags():
    """Create feature flags for Help Center functionality"""
    db: Session = SessionLocal()
    
    try:
        # Check if flags already exist
        existing_flags = db.query(FeatureFlag).filter(
            FeatureFlag.key.in_([
                "help_center_auto_publish",
                "help_center_notifications",
                "help_center_semantic_search"
            ])
        ).all()
        
        if existing_flags:
            print(f"Found {len(existing_flags)} existing feature flags. Skipping creation.")
            return
        
        flags = [
            {
                "key": "help_center_auto_publish",
                "name": "Help Center Auto-Publish",
                "description": "Automatically publish articles when updated via API with auto_publish=true parameter",
                "is_enabled": False,
                "rollout_percentage": 0,
                "environment": "production",
                "metadata_": {
                    "module": "help_center",
                    "category": "content_management",
                    "impact": "medium"
                }
            },
            {
                "key": "help_center_notifications",
                "name": "Help Center Notifications",
                "description": "Send notifications to subscribers when new articles are published",
                "is_enabled": True,
                "rollout_percentage": 100,
                "environment": "production",
                "metadata_": {
                    "module": "help_center",
                    "category": "notifications",
                    "impact": "low"
                }
            },
            {
                "key": "help_center_semantic_search",
                "name": "Help Center Semantic Search",
                "description": "Enable semantic vector search for better article discovery",
                "is_enabled": True,
                "rollout_percentage": 100,
                "environment": "production",
                "metadata_": {
                    "module": "help_center",
                    "category": "search",
                    "impact": "high",
                    "requires_embedding_service": True
                }
            }
        ]
        
        for flag_data in flags:
            flag = FeatureFlag(**flag_data)
            db.add(flag)
        
        db.commit()
        print(f"✓ Created {len(flags)} feature flags for Module 15")
        
        for flag_data in flags:
            status = "ENABLED" if flag_data["is_enabled"] else "DISABLED"
            print(f"  - {flag_data['key']}: {status}")
    
    except Exception as e:
        db.rollback()
        print(f"✗ Error seeding feature flags: {e}")
    
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding Module 15 feature flags...")
    seed_help_center_feature_flags()
