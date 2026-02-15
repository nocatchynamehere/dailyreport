# Project Initialization (2/14/2026):

The steps that were taken to start this file involve:

## 1) Created the project folder
```bash
mkdir dailyreport
cd dailyreport
git init
```

## 2) uv was chosen to do this project as it is gaining traction in the online community
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Restart the shell after installation.  uv verison 0.10.2 was used for this project.

## 3) Create the virtual enviroment
```bash
uv init
uv python install 3.12
uv venv --python 3.12
```
Activate the environment:
```bash
source .venv/bin/activate
```
Check and verify cli displays:
```bash
(dailyreport) username@computer:~/directory$
```

## 4) Add dependencies:
```bash
uv add pandas openpyxl psycopg[binary] python-dotenv pydantic
```
- pandas: structured data manipulation
    - reading excel into tables
    - handling missing values
    - computing duration
    - filtering by date
    - grouping for reports
    - sanity checking columns
- openpyxl: engine for reading .xlsx
    - we want to read .xlsx directly instead of .csv files
- psycopg[binary]: talks to PostgreSQL
    - inserting rows
    - transactions
    - queries
    - change approvals
    - audit logging
- python-dotenv: secrets
    - enables private information
    - hiding stuff from github
- pydantic: make configuration and data contracts strict
    - data validation
    - env vars exist
    - types are correct
    - formats are correct

## 5) Make .gitignore
A .gitignore is included to prevent committing:
- virtual environments
- secrets
- local spreadsheets
- generated outputs

## 6) Make local data folder
```bash
mkdir -p data/raw
```

## 7) Create .env for personal information needed for project
```bash
code .env
```
Include things like database login info (example):
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=time_tracker
DB_USER=postgres
DB_PASSWORD=password
```

## 8) Add Postgres via Docker (example):
Create docker-compose.yml:
```yaml
services:
    db:
        image: postgres:16
        environment:
            POSTGRES_DB: time_tracker
            POSTGRES_USER: postgres
            POSTGRES_PASSWORD: postgres
        ports:
            - "5432:5432"
        volumes:
            - pgdata:/var/lib/postgresql/data

volumes:
    pgdata:
```
Run it:
```bash
docker compose up -d
```