# Database Schema Initialization (2/16/2026)

## Database Acronym and Abbreviation Refresher

PK - Primary Key
UUID - Universally Unique Identifier
FK - Foreign Key

## 1) Talking through the schema

We are going to start out with three tables.  One table to hold the facts, one to hold the audit log, and one to hold edit requests.

### Table 1 - time_entries
This table will hold the actual data we are keeping track of in terms of our daily activities.  We need to make sure to add just enough constraint so that the table doesn't get flooded with bad data.  This table will be the source of truth for our reporting.

Table 1 Schema
- id - UUID PK
    - Has to be separate from excel id for safe merging and replication later.  No "id collisions."
- user_id - UUID NOT NULL FK
    - who the data is attributing to
    - allows for multiple entity tracking at a later date
- source_entry_id - INT NOT NULL
    - the excel entry id
    - tracks already entered information
    - helps with no id collisions by keeping it separate
- life_bucket_id - FK NOT NULL
    - category bucket (work, upkeep, sleep, dicking_around, health)
- activity_id - UUID NOT NULL
    - activity perfomed during category
    - try to keep to a curated list
- project_id - UUID NULL
    - optional project attribution
    - most entries won't be projects but this allows project tracking
- start_ts - TIMESTAMPTZ NOT NULL
    - obvious
- end_ts - TIMESTAMPTZ NOT NULL
    - obvious
- duration_minutes - INT NOT NULL
    - computed duration
    - reporting speed
- reporting_day - DATE GENERATED ALWAYS AS ((start_ts - INTERVAL '6 hours')::date) STORED
    - the day this entry is attributed to for daily reporting (6 AM cutover)
    - generated
        - makes reporting consistent and fast
        - ensures reporting day is derived from the canonical timestamp, not from Excel user input
        - avoids bugs where date is typed wrong in excel
- notes - TEXT NULL
    - free-form details
- created_by - TEXT NOT NULL (later FK to users)
    - person who recorded the entry
    - later accountable to a users table
- import_id - FK NOT NULL
    - which import batch inserted this row
    - traceability, re-import prevention, debugging, and audit context
- created_at - TIMESTAMPTZ NOT NULL DEFAULT now()
    - TIMESTAMPTZ = timestamp with timezone
    - when db row was created
    - now() is postgres server time

Constraints
- UNIQUE (user_id, source_entry_id)
    - prevents duplicate imports of the same excel row
    - idempotency anchor
- CHECK (source_entry_id > 0)
    - checks for sane entry id
- CHECK (end_ts > start_ts)
    - we intend to validate on a daily basis with no overlaps or weird spans
- CHECK (duration_minutes > 0)
    - checks for sane minutes calculation
- CHECK (duration_minutes < 24*60)
    - checks for sane minutes calculation
- CHECK (length(trim(created_by)) > 0)
    - enforces no empty strings

Foreign Keys
- FK (user_id, activity_id) -> activities(user_id, id)
- FK user_id -> users(id)
- FK import_id -> imports(id)
- FK life_bucket_id -> life_buckets(id)
- FK project_id -> projects(id)
    - if project_id is not NULL, (project_id, user_id) must exist in project_members

Indexes

These aim to speed up reads at the cost of slowing down writes.  Useful for common queries as relating to reporting.  With such a small dataset, that shouldn't be an issue.  We're adding indexes because they match expected query patterns and because this is portfolio-quality practice, not because we're prematurely optimizing.
- INDEX (user_id, reporting_day)
    - speeds up the core daily report query pattern:
        ```sql
        WHERE user_id = ? AND reporting_day = ?
        ```
    - this is the most common access path for generating yesterday's report for UserX
- INDEX (user_id, start_ts)
    - speeds up time range and debugging queries like:
        ```sql
        WHERE user_id = ? AND start_ts >= ? AND start_ts < ?
        ```
    - useful for investigating a specific window of time or troubleshooting ingest issues
- INDEX (import_id)
    - speeds up operational/audit queries like:
        ```sql
        WHERE import_id = ?
        ```
    - useful for reviewing exactly what a single import batch inserted (or for rolling back later)

### Table 2 - imports
This table tracks each ingestion batch.  It stores metadata and outcomes so the system can be:
- Traceable - know exactly which file produced which rows
- Idempotent - avoid double importing the same file
- Auditable - prove what happened and when
- Debuggable - see failures and counts without reading logs

time_entries.import_id will reference imports.id so every row can be tied back to the batch that created it.

Table 2 Schema
- id - UUID PK
- user_id - UUID NOT NULL FK
- file_name - TEXT NOT NULL
    - name of ingested file
    - supports multi user later
- file_hash - TEXT NOT NULL
    - deterministic hash of the files contents
    - if the same file is processed twice, the hash will match and you can block it cleanly
- imported_at - TIMESTAMPTZ NOT NULL DEFAULT now()
    - when the import record was batched
- imported_by - TEXT NOT NULL
    - who ran the import (human or service account)
- rows_seen - INT NOT NULL
    - how many rows in excel
- rows_inserted - INT NOT NULL
    - how many made it into time_entries
- rows_rejected - INT NOT NULL
    - validation failures
- status - TEXT NOT NULL
    - success/failed
- error_message - TEXT NULL
    - store the failure reason if status=FAILED

Constraints
- UNIQUE (user_id, file_hash)
    - prevents importing the same file contents twice for the same user
- CHECK (length(trim(file_name)) > 0)
- CHECK (length(trim(imported_by)) > 0)
    - prevent empty strings
    - keeps data clean
- CHECK (rows_seen >= 0 AND rows_inserted >= 0 AND rows_rejected >= 0)
    - row counts should never be negative
    - catches coding bugs immediately
- CHECK (rows_inserted + rows_rejected <= rows_seen)
    - can't insert/reject more rows than you read
    - also catches accounting bugs in ingestion logic
- CHECK (status IN ('SUCCESS','FAILED'))

Foreign Keys
- FK user_id -> users(id)

Indexes
- INDEX (user_id, imported_at)
    - supports the most common query, "show me recent imports for this user":
        ```sql
        WHERE user_id = ? ORDER BY imported_at DESC LIMIT 10
        ```
    - useful for monitoring, troubleshooting, and building a future import history view

### Table 3 - life_buckets
This is defining life buckets categories.

Table 3 Schema
- id - SMALLINT PK
    - SMALLINT is a compact integer type
    - can safely reference bucket IDs in code/config without worrying about name changes
- name - TEXT NOT NULL UNIQUE 
    - work/upkeep/sleep/dicking_around/health
    - protects against duplicate labels splitting reporting (i.e. work and Work)

Constraints

- CHECK (length(trim(name)) > 0)
    - no empty string names
- CHECK (name = lower(name))
    - only stores lowercase names

### Table 4 - activities
Defines per-user activity names used in time logging.  Referenced by time_entries.activity_id.  Keeping activities scoped prevents cross-user naming conflicts and supports independent evolution of each user's activity taxonomy.

Table 4 Schema
- id - UUID PK
- user_id - UUID NOT NULL FK
    - who the activities list belongs to
- name - TEXT NOT NULL
    - activity label
- is_active - BOOL NOT NULL DEFAULT TRUE
    - soft-disable activities without breaking historical references
- created_at - TIMESTAMPTZ NOT NULL DEFAULT now()
    - audit/debugging, and useful later for UI sorting

Contraints
- UNIQUE (user_id, name)
    - prevents duplicate activity names within a user
    - allows multiple users to have identical names
- UNIQUE (user_id, id)
    - required so that time_entries can define a composite foreign key
    - ensures an activity ID is only valid within the same user scope
- CHECK (length(trim(name)) > 0)
- CHECK (name = lower(name))

Foreign Keys
- FK user_id -> users(id)

### Table 5 - projects
This is for defining projects.

Table 5 Schema
- id - UUID PK
- name - TEXT NOT NULL UNIQUE
    - project names are a global namespace, must be unique
- is_active - BOOL NOT NULL DEFAULT TRUE
    - allows archiving without breaking historical references
- created_at - TIMESTAMPTZ NOT NULL DEFAULT now()
- created_by_user_id - UUID NOT NULL FK

Constraints
- CHECK (length(trim(name)) > 0)
- CHECK (name = lower(name))

Foreign Keys
- FK created_by_user_id -> users(id)

### Table 6 - project_members
This table handles permissions for projects.

Table 6 Schema
- project_id - UUID NOT NULL
- user_id - UUID NOT NULL
- role - TEXT NOT NULL DEFAULT 'member'
- added_at - TIMESTAMPTZ NOT NULL DEFAULT now()

Constraints
- CHECK (role IN ('owner', 'member', 'viewer'))

Primary Key
- PK (project_id, user_id)

Foreign Keys
- FK project_id -> projects(id)
- FK user_id -> users(id)

### Table 7 - audit_log
This keeps track of audits done.  It is trigger written.

Table 7 Schema
- id - UUID PK
- table_name - TEXT NOT NULL
- row_id - UUID NOT NULL
- action - TEXT NOT NULL (INSERT/UPDATE/DELETE)
- changed_at - TIMESTAMPTZ NOT NULL DEFAULT now()
- changed_by_user_id UUID NULL
- before JSONB - JSONB NULL
- after JSONB - JSONB NULL
- request_id - UUID NULL
- import_id - UUID NULL

Constraints
- CHECK (action IN ('INSERT', 'UPDATE', 'DELETE'))
- CHECK (length(trim(table_name)) > 0)
- CHECK (before IS NOT NULL OR after IS NOT NULL)
    - don't allow empty audits
- CHECK (action <> 'INSERT' OR before IS NULL)
    - if action is INSERT: before should be NULL
- CHECK (action <> 'DELETE' OR after IS NULL)
    - if action is DELETE: after should be NULL

Foreign Keys
- FK changed_by_user_id -> users(id)
- FK request_id -> edit_requests(id)
- FK import_id -> imports(id)

Indexes
- INDEX (table_name, row_id, changed_at DESC)
    - fetch history for a row
- INDEX (changed_at DESC)
    - recent changes
- INDEX (request_id)
    - tie approvals to applied changes
- INDEX (import_id)
    - show what an import changed

### Table 8 - edit_requests
This table keeps track of edit requests

Table 8 Schema
- id - UUID PK
- user_id - (who it impacts)
- target_table, target_row_id
- status (pending/approved/rejected)
- requested_by, requested_at
- reviewed_by, reviewed_at
- reason
- patch JSONB (the proposed changes)

### Table 9 - users
Defines system users.  Referenced to enforce multi-user data isolation.

Table 9 Schema
- id - UUID PK
- username - TEXT NOT NULL UNIQUE
- is_active - BOOL NOT NULL DEFAULT TRUE
- created_at - TIMESTAMPTZ NOT NULL DEFAULT now()

Constraints
- CHECK (length(trim(username)) > 0)
- CHECK (username = lower(username))