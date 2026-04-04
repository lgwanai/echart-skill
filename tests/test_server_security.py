"""Tests for server security features."""

import pytest
import os
import sys
import tempfile

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestPathTraversalValidation:
    """Test path traversal protection in validate_file_path."""

    def test_valid_path_within_base(self):
        """Valid paths within base directory should be allowed."""
        import validators
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            # Resolve the real path (macOS symlinks /var to /private/var)
            resolved_base = str(Path(tmpdir).resolve())

            # Create a test file
            test_file = os.path.join(tmpdir, "test.html")
            with open(test_file, 'w') as f:
                f.write("<html>test</html>")

            result = validators.validate_file_path(test_file, tmpdir)
            assert result.startswith(resolved_base)

    def test_path_traversal_blocked(self):
        """Path traversal attempts should be blocked."""
        import validators

        with tempfile.TemporaryDirectory() as tmpdir:
            # Try to access /etc/passwd via path traversal
            malicious_path = os.path.join(tmpdir, "..", "..", "etc", "passwd")

            with pytest.raises(ValueError, match="不在允许的目录"):
                validators.validate_file_path(malicious_path, tmpdir)

    def test_absolute_path_outside_blocked(self):
        """Absolute paths outside base directory should be blocked."""
        import validators

        with tempfile.TemporaryDirectory() as tmpdir:
            # Try to access /etc/passwd directly
            with pytest.raises(ValueError, match="不在允许的目录"):
                validators.validate_file_path("/etc/passwd", tmpdir)

    def test_nested_path_within_base_allowed(self):
        """Nested paths within base directory should be allowed."""
        import validators
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            # Resolve the real path (macOS symlinks /var to /private/var)
            resolved_base = str(Path(tmpdir).resolve())

            # Create nested directory structure
            nested_dir = os.path.join(tmpdir, "assets", "js")
            os.makedirs(nested_dir, exist_ok=True)
            test_file = os.path.join(nested_dir, "test.js")
            with open(test_file, 'w') as f:
                f.write("console.log('test');")

            result = validators.validate_file_path(test_file, tmpdir)
            assert result.startswith(resolved_base)

    def test_symlink_outside_blocked(self):
        """Symlinks pointing outside base directory should be blocked."""
        import validators

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a symlink to /etc/passwd
            symlink_path = os.path.join(tmpdir, "malicious_link")
            try:
                os.symlink("/etc/passwd", symlink_path)
            except (OSError, NotImplementedError):
                # Symlink creation might fail on some systems
                pytest.skip("Cannot create symlink on this system")

            with pytest.raises(ValueError, match="不在允许的目录"):
                validators.validate_file_path(symlink_path, tmpdir)
