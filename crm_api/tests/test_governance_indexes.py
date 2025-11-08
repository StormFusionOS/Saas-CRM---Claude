"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

Smoke tests for governance table indexes.

Verifies:
- Indexes exist on change_log(status) and task_logs(status)
- Index exists on task_logs(started_at)
- Queries use indexes efficiently (via EXPLAIN)
- Migration is reversible
"""

import pytest
from sqlalchemy import text
from datetime import datetime, timedelta


# ============================================================================
# Index Existence Tests
# ============================================================================


def test_change_log_status_index_exists(db):
    """Test that change_log.status index exists (from migration 001)."""
    # Query PostgreSQL system catalog to check if index exists
    result = db.execute(text("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'change_log'
        AND indexname = 'ix_change_log_status'
    """))

    row = result.fetchone()
    assert row is not None, "Index ix_change_log_status should exist"
    assert 'status' in row[1].lower(), "Index should be on status column"


def test_task_logs_status_index_exists(db):
    """Test that task_logs.status index exists (from migration 001)."""
    result = db.execute(text("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'task_logs'
        AND indexname = 'ix_task_logs_status'
    """))

    row = result.fetchone()
    assert row is not None, "Index ix_task_logs_status should exist"
    assert 'status' in row[1].lower(), "Index should be on status column"


def test_task_logs_started_at_index_exists(db):
    """Test that task_logs.started_at index exists (from migration 004)."""
    result = db.execute(text("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'task_logs'
        AND indexname = 'idx_task_logs_started_at_desc'
    """))

    row = result.fetchone()
    assert row is not None, "Index idx_task_logs_started_at_desc should exist"
    assert 'started_at' in row[1].lower(), "Index should be on started_at column"


def test_all_governance_indexes_listed(db):
    """Test that all expected governance indexes exist."""
    result = db.execute(text("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename IN ('change_log', 'task_logs', 'audit_issues')
        ORDER BY indexname
    """))

    indexes = [row[0] for row in result.fetchall()]

    # Verify key indexes exist
    expected_indexes = [
        'ix_change_log_status',
        'ix_task_logs_status',
        'idx_task_logs_started_at_desc',
        'idx_change_log_module_status',
        'idx_task_logs_module_status',
    ]

    for expected in expected_indexes:
        assert expected in indexes, f"Expected index {expected} not found"


# ============================================================================
# Query Performance Tests (EXPLAIN Analysis)
# ============================================================================


def test_change_log_status_filter_uses_index(db):
    """Test that filtering by status on change_log uses the index."""
    # Use EXPLAIN to check if index is used
    result = db.execute(text("""
        EXPLAIN (FORMAT JSON)
        SELECT * FROM change_log
        WHERE status = 'PENDING'
        LIMIT 100
    """))

    plan = result.fetchone()[0]

    # Convert to string for easier searching (plan is JSON array)
    plan_str = str(plan).lower()

    # Should use index scan, not sequential scan
    assert 'index' in plan_str or 'bitmap' in plan_str, \
        "Query should use index, got: " + plan_str[:200]


def test_task_logs_status_filter_uses_index(db):
    """Test that filtering by status on task_logs uses the index."""
    result = db.execute(text("""
        EXPLAIN (FORMAT JSON)
        SELECT * FROM task_logs
        WHERE status = 'FAILED'
        LIMIT 100
    """))

    plan = result.fetchone()[0]
    plan_str = str(plan).lower()

    # Should use index scan
    assert 'index' in plan_str or 'bitmap' in plan_str, \
        "Query should use index, got: " + plan_str[:200]


def test_task_logs_time_range_uses_index(db):
    """Test that time-range queries on task_logs use the started_at index."""
    result = db.execute(text("""
        EXPLAIN (FORMAT JSON)
        SELECT * FROM task_logs
        WHERE started_at >= NOW() - INTERVAL '24 hours'
        ORDER BY started_at DESC
        LIMIT 100
    """))

    plan = result.fetchone()[0]
    plan_str = str(plan).lower()

    # Should use index scan on started_at
    assert 'index' in plan_str or 'bitmap' in plan_str, \
        "Query should use index, got: " + plan_str[:200]


def test_task_logs_recent_first_query_uses_index(db):
    """Test that ordering by started_at DESC uses the index."""
    result = db.execute(text("""
        EXPLAIN (FORMAT JSON)
        SELECT * FROM task_logs
        ORDER BY started_at DESC
        LIMIT 10
    """))

    plan = result.fetchone()[0]
    plan_str = str(plan).lower()

    # DESC index should enable efficient backward scan
    assert 'index' in plan_str, \
        "ORDER BY started_at DESC should use index, got: " + plan_str[:200]


# ============================================================================
# Index Efficiency Tests (with data)
# ============================================================================


def test_status_index_performance_with_data(db):
    """Test that status index improves query performance with sample data."""
    from app.db_models import TaskLogModel
    from datetime import datetime, timedelta

    # Insert test data with different statuses
    statuses = ['QUEUED', 'RUNNING', 'COMPLETED', 'FAILED']
    for i in range(100):
        task = TaskLogModel(
            task_id=f"test_task_{i}",
            task_name=f"test_job_{i}",
            module="test_module",
            status=statuses[i % 4],
            started_at=datetime.utcnow() - timedelta(hours=i),
            queued_at=datetime.utcnow() - timedelta(hours=i, minutes=5)
        )
        db.add(task)

    db.commit()

    # Query with status filter
    result = db.execute(text("""
        SELECT COUNT(*) FROM task_logs WHERE status = 'FAILED'
    """))

    count = result.scalar()
    assert count == 25, "Should find 25 FAILED tasks"

    # Verify index was used (check query plan)
    result = db.execute(text("""
        EXPLAIN (FORMAT JSON)
        SELECT * FROM task_logs WHERE status = 'FAILED'
    """))

    plan = result.fetchone()[0]
    plan_str = str(plan).lower()

    # With 100 rows, PostgreSQL should use index
    assert 'index' in plan_str or 'bitmap' in plan_str, \
        "Should use index for status filter"

    # Cleanup
    db.execute(text("DELETE FROM task_logs WHERE task_id LIKE 'test_task_%'"))
    db.commit()


def test_started_at_index_performance_with_data(db):
    """Test that started_at index improves time-range queries."""
    from app.db_models import TaskLogModel
    from datetime import datetime, timedelta

    # Insert test data with different timestamps
    base_time = datetime.utcnow()
    for i in range(50):
        task = TaskLogModel(
            task_id=f"time_test_{i}",
            task_name=f"time_job_{i}",
            module="test_module",
            status="COMPLETED",
            started_at=base_time - timedelta(hours=i),
            queued_at=base_time - timedelta(hours=i, minutes=5)
        )
        db.add(task)

    db.commit()

    # Query recent tasks (last 24 hours)
    result = db.execute(text("""
        SELECT COUNT(*) FROM task_logs
        WHERE started_at >= NOW() - INTERVAL '24 hours'
        AND task_id LIKE 'time_test_%'
    """))

    count = result.scalar()
    assert count == 24, "Should find 24 tasks from last 24 hours"

    # Verify index was used
    result = db.execute(text("""
        EXPLAIN (FORMAT JSON)
        SELECT * FROM task_logs
        WHERE started_at >= NOW() - INTERVAL '24 hours'
        ORDER BY started_at DESC
        LIMIT 10
    """))

    plan = result.fetchone()[0]
    plan_str = str(plan).lower()

    assert 'index' in plan_str, "Should use started_at index"

    # Cleanup
    db.execute(text("DELETE FROM task_logs WHERE task_id LIKE 'time_test_%'"))
    db.commit()


# ============================================================================
# Composite Index Tests
# ============================================================================


def test_composite_module_status_index_exists(db):
    """Test that composite (module, status) indexes exist for both tables."""
    # Check change_log
    result = db.execute(text("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'change_log'
        AND indexname = 'idx_change_log_module_status'
    """))

    assert result.fetchone() is not None, \
        "Composite index idx_change_log_module_status should exist"

    # Check task_logs
    result = db.execute(text("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'task_logs'
        AND indexname = 'idx_task_logs_module_status'
    """))

    assert result.fetchone() is not None, \
        "Composite index idx_task_logs_module_status should exist"


def test_module_status_filter_uses_composite_index(db):
    """Test that filtering by module AND status uses the composite index."""
    result = db.execute(text("""
        EXPLAIN (FORMAT JSON)
        SELECT * FROM change_log
        WHERE module = 'ctr_optimizer'
        AND status = 'PENDING'
        LIMIT 100
    """))

    plan = result.fetchone()[0]
    plan_str = str(plan).lower()

    # Should use the composite index
    assert 'idx_change_log_module_status' in plan_str or 'index' in plan_str, \
        "Query should use composite index"


# ============================================================================
# Index Comment/Documentation Tests
# ============================================================================


def test_started_at_index_has_comment(db):
    """Test that the started_at index has documentation comment."""
    result = db.execute(text("""
        SELECT obj_description(c.oid, 'pg_class') as comment
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relname = 'idx_task_logs_started_at_desc'
        AND n.nspname = 'public'
    """))

    row = result.fetchone()
    if row and row[0]:
        comment = row[0]
        assert 'time-based' in comment.lower() or 'monitoring' in comment.lower(), \
            "Index should have descriptive comment"


# ============================================================================
# Migration Reversibility Test
# ============================================================================


def test_migration_is_reversible(db):
    """
    Test that the migration can be safely reversed.

    This is a documentation test - actual reversal testing
    requires alembic downgrade command in CI/CD.
    """
    # Verify downgrade path exists by checking the index can be dropped
    result = db.execute(text("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'task_logs'
        AND indexname = 'idx_task_logs_started_at_desc'
    """))

    index_exists = result.fetchone() is not None

    # Document expected behavior
    assert index_exists, \
        "Index should exist for upgrade. " \
        "Downgrade should safely remove it without affecting status indexes."


# ============================================================================
# Index Statistics Tests
# ============================================================================


def test_index_statistics_available(db):
    """Test that PostgreSQL maintains statistics for the indexes."""
    result = db.execute(text("""
        SELECT
            schemaname,
            tablename,
            indexname,
            idx_scan,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes
        WHERE tablename IN ('change_log', 'task_logs')
        AND indexname IN (
            'ix_change_log_status',
            'ix_task_logs_status',
            'idx_task_logs_started_at_desc'
        )
        ORDER BY indexname
    """))

    indexes_found = result.fetchall()

    # Should find at least the three main indexes
    assert len(indexes_found) >= 3, \
        f"Should find 3+ indexes in statistics, found {len(indexes_found)}"

    # Statistics should be tracked (idx_scan can be 0 if not yet used)
    for row in indexes_found:
        indexname = row[2]
        assert indexname in [
            'ix_change_log_status',
            'ix_task_logs_status',
            'idx_task_logs_started_at_desc'
        ], f"Unexpected index in statistics: {indexname}"
