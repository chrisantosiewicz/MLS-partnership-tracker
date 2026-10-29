"""Build the DuckDB database from scratch and run every data-quality test.

Usage (from the repo root):
    python python/build.py

Steps:
  1. Delete and recreate tracker.duckdb, so every run starts clean (running
     twice gives the same result).
  2. Run sql/schema.sql (creates tables), sql/load.sql (loads data/), then
     every sql/models/*.sql in file-name order (10_, 20_, ...).
  3. Run each tests/*.sql file. A test is a query that returns the rows that
     break a rule, so a passing test returns zero rows.
       test_*.sql  must return zero rows, or the build fails.
       warn_*.sql  rows are printed as a warning but don't fail the build
                   (for known gaps we track but shouldn't block the site).
  4. Exit with code 1 if any test_ file returned rows or any file failed to
     run. GitHub Actions treats a non-zero exit as a failed job.
"""

import sys
import duckdb

import config

REPO_ROOT = config.REPO_ROOT
DB_PATH = REPO_ROOT / "tracker.duckdb"
SQL_DIR = REPO_ROOT / "sql"
TESTS_DIR = REPO_ROOT / "tests"


def build_database() -> duckdb.DuckDBPyConnection:
    """Recreate the database and run the build SQL files in order."""
    if DB_PATH.exists():
        DB_PATH.unlink()

    # Run from the repo root so paths like 'data/partnerships.csv' in
    # load.sql resolve the same way on your laptop and in Actions.
    con = duckdb.connect(str(DB_PATH))
    con.execute(f"SET file_search_path = '{REPO_ROOT.as_posix()}'")

    # Empty raw files let the build run before the first ingestion.
    config.ensure_raw_files()

    build_files = [SQL_DIR / "schema.sql", SQL_DIR / "load.sql"]
    build_files += sorted((SQL_DIR / "models").glob("*.sql"))
    for path in build_files:
        print(f"build  {path.relative_to(REPO_ROOT)}")
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

        is_warning = path.name.startswith("warn_")
        if bad_rows.empty:
            print(f"PASS   {path.name}")
        elif is_warning:
            print(f"WARN   {path.name}: {len(bad_rows)} row(s)")
            print(bad_rows.head(10).to_string(index=False))
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
