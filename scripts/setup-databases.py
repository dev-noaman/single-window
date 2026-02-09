#!/usr/bin/env python3
"""
PostgreSQL setup for officernd and scrape-sw-codes:
- Creates users and databases (officernd, codesdb)
- Optionally creates OfficeRnD tables when officernd path is provided

Idempotent: safe to run multiple times.
Usage:
  python3 setup-databases.py                    # users + databases only
  python3 setup-databases.py /path/to/officernd  # users + databases + officernd tables
"""
import importlib.util
import os
import subprocess
import sys

DEFAULT_DATABASE_URL = "postgresql://officernd_user:OfficerndPass2024@localhost:5432/officernd"


def run_psql(sql: str) -> tuple[str, int]:
    """Run SQL as postgres user via sudo. Returns (stdout+stderr, exit_code)."""
    result = subprocess.run(
        ["sudo", "-u", "postgres", "psql", "-tc", sql],
        capture_output=True,
        text=True,
    )
    out = (result.stdout or "") + (result.stderr or "")
    return out.strip(), result.returncode


def run_psql_cmd(sql: str) -> bool:
    """Run SQL as postgres user. Returns True on success."""
    result = subprocess.run(
        ["sudo", "-u", "postgres", "psql", "-c", sql],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def user_exists(user: str) -> bool:
    out, _ = run_psql(f"SELECT 1 FROM pg_roles WHERE rolname='{user}'")
    return "1" in out


def db_exists(db: str) -> bool:
    out, _ = run_psql(f"SELECT 1 FROM pg_database WHERE datname='{db}'")
    return "1" in out


def create_users_and_databases() -> None:
    configs = [
        ("officernd_user", "OfficerndPass2024", "officernd"),
        ("codesuser", "CodesPass2024", "codesdb"),
    ]

    for user, password, db in configs:
        if not user_exists(user):
            if run_psql_cmd(f"CREATE USER {user} WITH PASSWORD '{password}';"):
                print(f"Created user {user}")
            else:
                print(f"Failed to create user {user}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"User {user} already exists")

        if not db_exists(db):
            if run_psql_cmd(f"CREATE DATABASE {db} OWNER {user};"):
                print(f"Created database {db}")
            else:
                print(f"Failed to create database {db}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Database {db} already exists")

    print("Databases ready")


def create_officernd_tables(officernd_path: str) -> None:
    if not os.path.isdir(officernd_path):
        print(f"Error: {officernd_path} is not a directory", file=sys.stderr)
        sys.exit(1)

    sys.path.insert(0, officernd_path)
    sys.modules["db"] = type(sys)("db")
    sys.modules["api"] = type(sys)("api")

    try:
        from sqlalchemy import create_engine, inspect, text
    except ImportError as e:
        print(f"Error: sqlalchemy not installed - {e}")
        sys.exit(1)

    env_path = os.path.join(officernd_path, "config", ".env")
    database_url = DEFAULT_DATABASE_URL
    if os.path.isfile(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("DATABASE_URL=") and not line.startswith("#"):
                    database_url = line.split("=", 1)[1].strip().strip("'\"")
                    # Script runs on the host, not in Docker
                    database_url = database_url.replace("host.docker.internal", "localhost")
                    break

    models_path = os.path.join(officernd_path, "db", "models.py")
    if not os.path.isfile(models_path):
        print(f"Error: models file not found at {models_path}")
        sys.exit(1)

    try:
        engine = create_engine(database_url)
    except Exception as e:
        print(f"Error: cannot create DB engine - {e}")
        sys.exit(1)

    try:
        spec = importlib.util.spec_from_file_location("db_models", models_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"Error: cannot load models from {models_path} - {e}")
        sys.exit(1)

    try:
        existing = inspect(engine).get_table_names()
    except Exception as e:
        print(f"Error: cannot connect to database ({database_url.split('@')[0]}@...) - {e}")
        sys.exit(1)

    before = len(existing)

    # Step 1: Create any new tables
    mod.Base.metadata.create_all(engine)
    after = len(inspect(engine).get_table_names())
    if after > before:
        print(f"Created {after - before} new table(s) ({after} total)")
    else:
        print(f"All {before} tables exist")

    # Step 2: Add missing columns to existing tables
    SA_TYPE_MAP = {
        "Text": "TEXT", "Integer": "INTEGER", "Float": "DOUBLE PRECISION",
        "Boolean": "BOOLEAN", "JSONB": "JSONB",
    }
    db_inspector = inspect(engine)
    added = 0
    for table in mod.Base.metadata.sorted_tables:
        if table.name not in existing:
            continue  # new table, already created above
        db_columns = {c["name"] for c in db_inspector.get_columns(table.name)}
        for col in table.columns:
            if col.name not in db_columns:
                type_name = type(col.type).__name__
                pg_type = SA_TYPE_MAP.get(type_name, "TEXT")
                if type_name == "DateTime" and getattr(col.type, "timezone", False):
                    pg_type = "TIMESTAMP WITH TIME ZONE"
                elif type_name == "DateTime":
                    pg_type = "TIMESTAMP"
                sql = f'ALTER TABLE "{table.name}" ADD COLUMN IF NOT EXISTS "{col.name}" {pg_type}'
                try:
                    with engine.begin() as conn:
                        conn.execute(text(sql))
                    added += 1
                    print(f"  Added column {table.name}.{col.name} ({pg_type})")
                except Exception as e:
                    print(f"  Failed to add {table.name}.{col.name}: {e}")
    if added:
        print(f"Migration: added {added} column(s)")
    else:
        print("Schema up to date (no missing columns)")


def main() -> None:
    create_users_and_databases()

    if len(sys.argv) >= 2:
        officernd_path = sys.argv[1]
        create_officernd_tables(officernd_path)


if __name__ == "__main__":
    main()
