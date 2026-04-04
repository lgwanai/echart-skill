"""Tests for ServerLifecycle class - process management with PID tracking."""

import pytest
import os
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta


class TestServerLifecycle:
    """Tests for server lifecycle management with PID tracking."""

    @pytest.fixture
    def temp_pid_dir(self):
        """Create a temporary directory for PID files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_pid_file_created(self, temp_pid_dir):
        """PID file should be created on server startup.

        Expected: ServerLifecycle.write_pid() creates a PID file
        containing the current process ID.
        """
        from scripts.server import ServerLifecycle

        lifecycle = ServerLifecycle(port=18001, pid_dir=temp_pid_dir)
        lifecycle.write_pid()

        # Check PID file exists
        assert lifecycle.pid_file.exists()

        # Check PID file contains correct PID
        pid = lifecycle.read_pid()
        assert pid == os.getpid()

        # Cleanup
        lifecycle.clear_pid()

    def test_pid_file_removed(self, temp_pid_dir):
        """PID file should be removed on clean shutdown.

        Expected: ServerLifecycle.clear_pid() removes the PID file
        and last_request file.
        """
        from scripts.server import ServerLifecycle

        lifecycle = ServerLifecycle(port=18002, pid_dir=temp_pid_dir)
        lifecycle.write_pid()
        lifecycle.update_last_request()

        # Verify files exist
        assert lifecycle.pid_file.exists()
        assert lifecycle.last_request_file.exists()

        # Clear PID files
        lifecycle.clear_pid()

        # Verify files are removed
        assert not lifecycle.pid_file.exists()
        assert not lifecycle.last_request_file.exists()

    def test_orphan_detection(self, temp_pid_dir):
        """Orphan processes should be detected and cleaned up.

        Expected: When PID file exists but process is dead,
        kill_orphan() cleans up the stale PID file.
        """
        from scripts.server import ServerLifecycle

        lifecycle = ServerLifecycle(port=18003, pid_dir=temp_pid_dir)

        # Write a fake PID that doesn't correspond to any process
        fake_pid = 99999999  # Very unlikely to be a real PID
        lifecycle.pid_file.write_text(str(fake_pid))

        # kill_orphan should detect the process doesn't exist and clean up
        result = lifecycle.kill_orphan()

        # Should return True (orphan was cleaned up)
        assert result is True

        # PID file should be removed
        assert not lifecycle.pid_file.exists()

    def test_timeout_shutdown(self, temp_pid_dir):
        """Timeout should trigger shutdown after inactivity.

        Expected: should_shutdown() returns True when last_request
        was more than 5 minutes ago.
        """
        from scripts.server import ServerLifecycle

        lifecycle = ServerLifecycle(port=18004, pid_dir=temp_pid_dir)

        # Set last_request to 6 minutes ago
        old_time = datetime.now() - timedelta(minutes=6)
        lifecycle.last_request_file.write_text(old_time.isoformat())

        # Should indicate shutdown needed
        assert lifecycle.should_shutdown() is True

        # Cleanup
        lifecycle.clear_pid()

    def test_no_timeout_recent_activity(self, temp_pid_dir):
        """No timeout when there is recent activity.

        Expected: should_shutdown() returns False when last_request
        was less than 5 minutes ago.
        """
        from scripts.server import ServerLifecycle

        lifecycle = ServerLifecycle(port=18005, pid_dir=temp_pid_dir)

        # Set last_request to 2 minutes ago (recent)
        recent_time = datetime.now() - timedelta(minutes=2)
        lifecycle.last_request_file.write_text(recent_time.isoformat())

        # Should NOT indicate shutdown
        assert lifecycle.should_shutdown() is False

        # Cleanup
        lifecycle.clear_pid()

    def test_is_server_active(self, temp_pid_dir):
        """Active server should be detected correctly.

        Expected: is_server_active() returns True for a running process,
        False for a non-existent process.
        """
        from scripts.server import ServerLifecycle

        lifecycle = ServerLifecycle(port=18006, pid_dir=temp_pid_dir)

        # Current process is always running
        assert lifecycle.is_server_active(os.getpid()) is True

        # Non-existent PID
        assert lifecycle.is_server_active(99999999) is False

    def test_update_last_request(self, temp_pid_dir):
        """Last request timestamp should be updated.

        Expected: update_last_request() writes current timestamp.
        """
        from scripts.server import ServerLifecycle

        lifecycle = ServerLifecycle(port=18007, pid_dir=temp_pid_dir)

        before = datetime.now()
        lifecycle.update_last_request()
        after = datetime.now()

        # Read the timestamp
        content = lifecycle.last_request_file.read_text()
        timestamp = datetime.fromisoformat(content)

        # Timestamp should be between before and after
        assert before <= timestamp <= after

        # Cleanup
        lifecycle.clear_pid()

    def test_read_pid_none_when_missing(self, temp_pid_dir):
        """read_pid should return None when PID file doesn't exist.

        Expected: No error when PID file is missing.
        """
        from scripts.server import ServerLifecycle

        lifecycle = ServerLifecycle(port=18008, pid_dir=temp_pid_dir)

        # PID file doesn't exist yet
        assert lifecycle.read_pid() is None

    def test_kill_orphan_no_file(self, temp_pid_dir):
        """kill_orphan should return False when no PID file exists.

        Expected: No error when PID file is missing.
        """
        from scripts.server import ServerLifecycle

        lifecycle = ServerLifecycle(port=18009, pid_dir=temp_pid_dir)

        # No PID file exists
        result = lifecycle.kill_orphan()

        # Should return False (nothing to clean)
        assert result is False
