# Daily Reporting Tool

This is a pipeline to show my girlfriend in the most intentionally over-engineered way what I do with my day.  I record my time in Excel, import that to PostgreSQL, then (eventually) turn that information into a report.

## We are using:
- Python 3.12
- uv for dependency management
- PostgreSQL (Docker)
- pandas / openpyxl

## Setup

### 1) Install dependencies
```bash
uv sync
```

### 2) Create environment file
```bash
cp .env.example .env
```
Then fill in the credentials.

### 3) Start Database
```bash
docker compose up -d
```

### 4) Verify database is hosted
```bash
docker ps
```

## Project Structure
src/ - application code
templates/ - spreadsheet input contracts
data/ - real local data (not committed)
docs/ - documentation