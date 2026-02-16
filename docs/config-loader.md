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