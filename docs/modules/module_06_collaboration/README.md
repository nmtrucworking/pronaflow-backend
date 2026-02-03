# Module 6: Unified Collaboration Hub

## Overview
Real-time collaboration and communication:
- Notifications and alerts
- Comments and discussions
- Activity streams
- Real-time updates
- Email notifications

## Key Components

### Models
- **Notification** - User notifications with read status
- **NotificationTemplate** - Email templates
- **NotificationPreference** - User notification settings
- **DomainEvent** - Event sourcing events
- **EventConsumer** - Event subscription tracking

### Services
- `NotificationService` - Notification delivery
- `ActivityService` - Activity tracking
- `EventBusService` - Event publishing/subscribing

## Database Tables (5)
- notifications
- notification_templates
- notification_preferences
- domain_events
- event_consumers

## Features
- Real-time notifications
- Email digests
- Activity timeline
- Mention and mention suggestions
- Notification preferences

