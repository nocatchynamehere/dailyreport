# Building a Config Loader (1/16/2026)

## 1) Make python packages importable
```bash
touch src/__init__.py
mkdir -p src/config src/db src/cli
touch src/config/__init__.py src/db/__init__.py src/cli/__init__.py
```
We do this because it tells python that these directories are to be treated like importable modules.
## 2) Write the settings loader
Create src/config/settings.py

This validates the data in our .env.  It makes sure that the essential variables exist and are typed correctly.  If not, program fails fast and with a clear error.  It returns our now typed and validated data in the form of a stored object.  Also, it exposes a property (db_dsn) that provides a ready to use connection string for database clients.

## 3) Write the database connection helper
Create src/db/connection.py

```python
from __future__ import annotations
import psycopg
from src.config.settings import Settings

def get_connection(settings: Settings) -> psycopg.Connection:
    return psycopg.connect(settings.db_dsn, autocommit=True)
```

This script establishes the single point of entry from our application to the database (PostgreSQL).  It makes interaction cleaner.  It also makes it to where if we need to change or add anything about the connection itself, we only have to change it in one place.  It is important to note that we started with autocommit=True because we want to keep things simple before controlling all transaction explicitly.

psycopg is a package that interacts with a database by creating a connection.  So, our connection.py takes our validated settings.db_dsn from the last step as inputs and outputs a connection object.

Also, as a refresher, from __future\_\_ import annotations means that instead of failing out because of type requirements early, the value will just be the hint stored as a string.

## 4) Write a CLI entrypoint with a check-db command
Create src/cli/main.py

A reminder of some unix standard use exit codes
- 0 = success
- 1 = general failure
- 2 = command usage error

cmd_check_db() tests our connection to the database and returns an error based on why the database isn't connecting, or displays a message upon a successful connection.  
- The only time it fails before the error handling is when the config is missing.  That is because we would like the program to crash out due to setup issues.
- We make sure to include 'with' so the connection is closed even if an exception happens.
- cursor is a "query executor" object tied to a connection
    - create cursor
    - execute SQL
    - fetch results
    - close cursor
- 'connection'.cursor().execute("select 1;")
    - sends SQL to postgres
    - 'select 1' is a classic health check: quick, tests the full pipeline, requires little to no resources
- 'connection'.cursor().fetchone()
    - returns one row, one column from result set
- Returning a value means:
    - query executed
    - result returned
    - cursor fetch works
- errors are caught, handled, and reported on
