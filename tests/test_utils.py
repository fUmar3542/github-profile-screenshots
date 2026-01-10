"""Unit tests for utility functions."""

import logging
from unittest.mock import MagicMock, patch

from src.utils import (
    cleanup_old_screenshots,
    ensure_directory_exists,
    generate_screenshot_filename,
    generate_timestamp,
    get_project_root,
    setup_logging,
)


class TestUtils:
    """Test cases for utility functions."""

    def test_setup_logging_default_level(self):
        """Test logger setup with default level."""
        logger = setup_logging()
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0

    def test_setup_logging_custom_level(self):
        """Test logger setup with custom level."""
        logger = setup_logging("DEBUG")
        assert logger.level == logging.DEBUG

    def test_generate_timestamp_format(self):
        """Test timestamp generation format."""
        timestamp = generate_timestamp()
        assert len(timestamp) == 19  # YYYY-MM-DD-HH-MM-SS
        assert timestamp.count("-") == 5

    @patch("src.utils.datetime")
    def test_generate_timestamp_fixed_time(self, mock_datetime):
        """Test timestamp generation with fixed time."""
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2024-01-15-10-30-45"
        mock_datetime.now.return_value = mock_now

        timestamp = generate_timestamp()
        assert timestamp == "2024-01-15-10-30-45"

    def test_generate_screenshot_filename_default(self):
        """Test screenshot filename generation with default timestamp."""
        filename = generate_screenshot_filename()
        # New format: YYYY-MM-DD.png (shorter for bio URLs)
        assert filename.endswith(".png")
        assert len(filename) == 14  # YYYY-MM-DD.png
        # Should match date pattern
        assert filename[4] == "-" and filename[7] == "-"

    def test_generate_screenshot_filename_custom_timestamp(self):
        """Test screenshot filename generation with custom timestamp."""
        # New format extracts date from timestamp
        filename = generate_screenshot_filename("2024-01-15-10-30-45")
        assert filename == "2024-01-15.png"

    def test_ensure_directory_exists_new(self, tmp_path):
        """Test directory creation when it doesn't exist."""
        test_dir = tmp_path / "test" / "nested" / "dir"
        ensure_directory_exists(test_dir)
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_ensure_directory_exists_existing(self, tmp_path):
        """Test directory creation when it already exists."""
        test_dir = tmp_path / "existing"
        test_dir.mkdir()
        ensure_directory_exists(test_dir)  # Should not raise
        assert test_dir.exists()

    def test_get_project_root(self):
        """Test getting project root directory."""
        root = get_project_root()
        assert root.exists()
        assert (root / "src").exists()

    def test_cleanup_old_screenshots_no_directory(self, tmp_path):
        """Test cleanup when directory doesn't exist."""
        non_existent = tmp_path / "non_existent"
        cleanup_old_screenshots(non_existent)  # Should not raise

    def test_cleanup_old_screenshots_keep_recent(self, tmp_path):
        """Test cleanup keeps most recent screenshots."""
        # Create test screenshots
        screenshots_dir = tmp_path / "screenshots"
        screenshots_dir.mkdir()

        screenshot_files = []
        for i in range(10):
            screenshot = screenshots_dir / f"screenshot-2024-01-{i+1:02d}-00-00-00.png"
            screenshot.touch()
            screenshot_files.append(screenshot)

        # Cleanup, keeping only 5
        cleanup_old_screenshots(screenshots_dir, keep_count=5)

        # Check that only 5 remain
        remaining = list(screenshots_dir.glob("screenshot-*.png"))
        assert len(remaining) == 5

    def test_cleanup_old_screenshots_fewer_than_keep_count(self, tmp_path):
        """Test cleanup when fewer screenshots than keep count."""
        screenshots_dir = tmp_path / "screenshots"
        screenshots_dir.mkdir()

        # Create 3 screenshots
        for i in range(3):
            screenshot = screenshots_dir / f"screenshot-{i}.png"
            screenshot.touch()

        # Try to keep 5
        cleanup_old_screenshots(screenshots_dir, keep_count=5)

        # All 3 should remain
        remaining = list(screenshots_dir.glob("screenshot-*.png"))
        assert len(remaining) == 3

    def test_cleanup_old_screenshots_ignores_other_files(self, tmp_path):
        """Test cleanup ignores files that don't match pattern."""
        screenshots_dir = tmp_path / "screenshots"
        screenshots_dir.mkdir()

        # Create screenshots
        for i in range(5):
            screenshot = screenshots_dir / f"screenshot-{i}.png"
            screenshot.touch()

        # Create other files
        other = screenshots_dir / "other.png"
        other.touch()

        # Cleanup
        cleanup_old_screenshots(screenshots_dir, keep_count=2)

        # Check other file still exists
        assert other.exists()
        # Check only 2 screenshots remain
        screenshots = list(screenshots_dir.glob("screenshot-*.png"))
        assert len(screenshots) == 2
