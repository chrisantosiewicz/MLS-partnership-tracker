"""Build the DuckDB database from scratch and run every data-quality test.

Usage (from the repo root):
    python python/run_tests.py

Steps:
  1. Delete and recreate tracker.duckdb, so every run starts clean (running
     twice gives the same result).
  2. Run sql/schema.sql (creates tables), then sql/load.sql if it exists
     (loads the CSVs).
  3. Run each tests/*.sql file. A test is a query that returns the rows that
     break a rule, so a passing test returns zero rows.
  4. Exit with code 1 if any test returned rows or failed to run. GitHub
     Actions treats a non-zero exit as a failed job.
"""

import sys
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "tracker.duckdb"
SQL_DIR = REPO_ROOT / "sql"
TESTS_DIR = REPO_ROOT / "tests"

# Run in this order. load.sql is optional until you write it.
BUILD_FILES = ["schema.sql", "load.sql"]


def build_database() -> duckdb.DuckDBPyConnection:
    """Recreate the database and run the build SQL files in order."""
    if DB_PATH.exists():
        DB_PATH.unlink()

    # Run from the repo root so paths like 'data/partnerships.csv' in
    # load.sql resolve the same way on your laptop and in Actions.
    con = duckdb.connect(str(DB_PATH))
    con.execute(f"SET file_search_path = '{REPO_ROOT.as_posix()}'")

    schema = SQL_DIR / "schema.sql"
    if not schema.exists():
        sys.exit("sql/schema.sql not found. Write it first, then rerun.")

    for name in BUILD_FILES:
        path = SQL_DIR / name
        if path.exists():
            print(f"build  {name}")
            con.execute(path.read_text())
    return con


def run_tests(con: duckdb.DuckDBPyConnection) -> bool:
    """Run each test file and report it. Returns True if all pass."""
    test_files = sorted(TESTS_DIR.glob("*.sql"))
    if not test_files:
        print("No tests found in tests/. Add some *.sql files.")
        return True

    all_passed = True
    for path in test_files:
        try:
            bad_rows = con.execute(path.read_text()).fetchdf()
        except duckdb.Error as err:
            print(f"ERROR  {path.name}: {err}")
            all_passed = False
            continue

        if bad_rows.empty:
            print(f"PASS   {path.name}")
        else:
            print(f"FAIL   {path.name}: {len(bad_rows)} row(s)")
            print(bad_rows.head(10).to_string(index=False))
            all_passed = False
    return all_passed


if __name__ == "__main__":
    connection = build_database()
    passed = run_tests(connection)
    connection.close()
    sys.exit(0 if passed else 1)
