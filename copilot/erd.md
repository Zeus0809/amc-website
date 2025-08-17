# Arlington Men's Circle Website - Entity Relationship Diagram

## Database ERD

```
┌─────────────────────────────────────┐
│                USERS                │
├─────────────────────────────────────┤
│ id (PK)          UUID               │
│ username         VARCHAR(50) UNIQUE │
│ email            VARCHAR(100) UNIQUE│
│ password_hash    VARCHAR(255)       │
│ first_name       VARCHAR(50)        │
│ last_name        VARCHAR(50)        │
│ is_active        BOOLEAN DEFAULT T  │
│ is_approved      BOOLEAN DEFAULT F  │
│ is_admin         BOOLEAN DEFAULT F  │
│ created_at       TIMESTAMP          │
└─────────────────────────────────────┘
                    │
                    │ (1:many)
                    ▼
          ┌─────────────────────────┐
          │         RSVPS           │ 
          │     (JOIN TABLE)        │
          ├─────────────────────────┤ 
          │ id (PK) UUID            │ 
          │ user_id (FK) → users.id │ 
          │ event_id (FK)→events.id │ 
          │ status VARCHAR(20)      │ 
          │ created_at TIMESTAMP    │ 
          │                         │ 
          │ UNIQUE(user_id,event_id)│ 
          └─────────────────────────┘           
                    ▲                           
                    │ (many:1)
                    │
┌──────────────────────────────────────┐
│               EVENTS                 │ 
├──────────────────────────────────────┤ 
│ id (PK) UUID                         │ 
│ title        VARCHAR(200)            │ 
│ description  TEXT                    │ 
│ date_time    TIMESTAMP               │ 
│ location     VARCHAR(200)            │ 
│ max_attendees INTEGER                │ 
│ created_at   TIMESTAMP               │ 
└──────────────────────────────────────┘           

RELATIONSHIPS:
• users ↔ events (many:many) : Many users can attend many events
  - Implemented via RSVP join table
• users → rsvps (1:many)     : One user can RSVP to many events  
• events → rsvps (1:many)    : One event can have many RSVPs
• user_id + event_id (unique): One user can only RSVP once per event

NOTES:
- RSVP table serves as the join table for Users ↔ Events many-to-many relationship
- No created_by field needed - events are manually created by admin
- Photos table omitted from MVP (will be added in Phase 2)
```

## Database Relationships Explained

### USERS Table (Central entity)
- Primary entity for authentication and user management
- Referenced by all other tables for ownership/attribution
- UUID primary key prevents user enumeration attacks

### EVENTS Table
- Stores all event information
- `created_by` links to `users.id` (who created the event)
- Independent entity that can exist without RSVPs or photos
- UUID primary key keeps event IDs unpredictable

### RSVPS Table (Junction/Bridge table)
- Links users to events (many-to-many relationship)
- `UNIQUE(user_id, event_id)` prevents duplicate RSVPs
- `status` field allows for different RSVP types (attending, maybe, not_attending)
- Acts as the core functionality for event attendance tracking

## Key Constraints

### Primary Keys
- All tables use UUID primary keys for security and scalability
- UUIDs prevent sequential ID enumeration attacks
- Better for distributed systems and database merging

### Foreign Key Constraints
- Maintain referential integrity across all relationships
- Ensure data consistency (can't RSVP to non-existent event)
- Cascade delete options can be configured as needed

### Unique Constraints
- `users.username` and `users.email` must be unique
- `rsvps(user_id, event_id)` prevents duplicate RSVPs per user per event
- Ensures data integrity and prevents duplicate entries

### NOT NULL Constraints
- Required fields are enforced at database level
- Prevents incomplete records
- Ensures all critical data is always present

### Default Values
- Timestamps automatically set on record creation
- Boolean flags have sensible defaults (e.g., `is_active = TRUE`)
- Reduces application complexity and ensures consistency

## Security Considerations

### UUID Benefits
- **Non-sequential:** Prevents user/event enumeration
- **Unpredictable:** Can't guess other users' IDs
- **Privacy:** Better for private group functionality
- **Scalable:** No collision issues across multiple servers

### Data Relationships
- Foreign key constraints prevent orphaned records
- User authentication required for all data access
- Event privacy maintained through user-based access control
- Photo uploads tied to authenticated users only

## Scalability Notes

This ERD design supports:
- **Current Scale:** 9-50 users with occasional events
- **Future Growth:** Can easily scale to hundreds of users
- **Performance:** Indexed foreign keys for fast queries
- **Flexibility:** Easy to add new tables/relationships as features grow

The structure is normalized to 3NF (Third Normal Form) to minimize data redundancy while maintaining query performance for the expected usage patterns of the Arlington Men's Circle website.
