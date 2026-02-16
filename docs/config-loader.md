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

This validates the data in our .env.
