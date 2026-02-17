# Database Schema Initialization (2/16/2026)

## 1) Talking through the schema

We are going to start out with three tables.  One table to hold the facts, one to hold the audit log, and one to hold edit requests.

### Table 1 - time_entries
This table will hold the actual data we are keeping track of in terms of our daily activities.  We need to make sure to add just enough constraint so that the table doesn't get flooded with bad data.

Table 1 Schema
- id - UUID PK
- source - TEXT NOT NULL (who is the data attributed to)
- source_entry_id - INT NOT NULL (excel entry_id)
- entry_date - DATE NOT NULL
- life_bucket_id - FK NOT NULL (life bucket)
- activity_id - FK NOT NULL (activity completed)
- project_id - FK NULL (mostly NULL but can be credited to a project)
- time_start - TIME NOT NULL
- time_end - TIME NOT NULL
- duration_minutes - INT
- notes - TEXT NULL (notes about entry)
- created_by - TEXT NOT NULL (later FK to users)
- import_id - FK NOT NULL
- created_at - TIMESTAMPTZ DEFAULT now()

Constraints
- UNIQUE (source, source_entry_id)
- CHECK (time_end > time_start)
- CHECK (duration_minutes > 0)

### Table 2 - imports
This is the staging table for validation before being input into time_entries.

Table 2 Schema
- id - UUID PK
- source - TEXT
- file_name - TEXT
- file_hash - TEXT
- imported_at - TIMESTAMPTZ DEFAULT now()
- imported_by - TEXT

### Table 3 - life_buckets
This is defining life buckets categories.

Table 3 Schema
- id - SMALLINT PK
- name - TEXT UNIQUE (work/upkeep/sleep/dicking_around/health)

### Table 4 - activities
This is for defining activities subcategories.

Table 4 Schema
- id - UUID PK
- name - TEXT UNIQUE
- is_active - BOOL DEFAULT TRUE

### Table 5 - projects
This is for defining projects.

Table 5 Schema
- id - UUID PK
- name - TEXT UNIQUE
- is_active - BOOL DEFAULT TRUE

### Table 6 - audit_log
This keeps track of audits done.  It is trigger written.

Table 6 Schema
- id - UUID PK
- table_name, row_id, action, changed_at, changed_by
- before JSONB, after JSONB
- request_id - NULLABLE FK to edit_requests (so changes link to approvals)

### Table 7 - edit_requests
This table keeps track of edit requests
- id - UUID PK
- source - (who it impacts)
- target_table, target_row_id
- status (pending/approved/rejected)
- requested_by, requested_at
- reviewed_by, reviewed_at
- reason
- patch JSONB (the proposed changes)