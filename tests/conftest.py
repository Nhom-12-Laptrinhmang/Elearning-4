import pytest


def pytest_sessionfinish(session, exitstatus):
    """Called after the whole test run finishes — we export the DB to SQL here."""
    try:
        # Import here to avoid side-effects at collection time
        from tests.test_main import export_to_sql
        export_to_sql()
        print('\n✅ Database exported after test session.')
    except Exception as e:
        print(f'\n⚠️ Failed to export DB after tests: {e}')
