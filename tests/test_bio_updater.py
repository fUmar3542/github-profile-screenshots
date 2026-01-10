"""Unit tests for bio updater module."""

from unittest.mock import MagicMock, patch

import pytest

from src.bio_updater import BioUpdater, update_github_bio


class TestBioUpdater:
    """Test cases for BioUpdater class."""

    def test_init(self):
        """Test initialization."""
        updater = BioUpdater("test_token", "testuser")
        assert updater.token == "test_token"
        assert updater.username == "testuser"
        assert updater.github is None
        assert updater.original_bio is None

    @patch("src.bio_updater.Github")
    def test_connect_success(self, mock_github):
        """Test successful GitHub connection."""
        mock_user = MagicMock()
        mock_user.login = "testuser"

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        updater = BioUpdater("test_token", "testuser")
        updater.connect()

        assert updater.github is not None
        mock_github.assert_called_once_with("test_token")

    @patch("src.bio_updater.Github")
    def test_connect_different_user_warning(self, mock_github):
        """Test connection with different authenticated user."""
        mock_user = MagicMock()
        mock_user.login = "different_user"

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        updater = BioUpdater("test_token", "testuser")
        updater.connect()  # Should log warning but not fail

        assert updater.github is not None

    @patch("src.bio_updater.Github")
    def test_get_current_bio(self, mock_github):
        """Test fetching current bio."""
        mock_user = MagicMock()
        mock_user.login = "testuser"
        mock_user.bio = "Current bio text"

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        updater = BioUpdater("test_token", "testuser")
        updater.connect()
        bio = updater.get_current_bio()

        assert bio == "Current bio text"
        assert updater.original_bio == "Current bio text"

    @patch("src.bio_updater.Github")
    def test_get_current_bio_empty(self, mock_github):
        """Test fetching empty bio."""
        mock_user = MagicMock()
        mock_user.login = "testuser"
        mock_user.bio = None

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        updater = BioUpdater("test_token", "testuser")
        updater.connect()
        bio = updater.get_current_bio()

        assert bio == ""

    @patch("src.bio_updater.Github")
    def test_update_bio_prepend(self, mock_github):
        """Test updating bio with prepend mode."""
        mock_user = MagicMock()
        mock_user.login = "testuser"
        mock_user.bio = "Existing bio"

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        updater = BioUpdater("test_token", "testuser")
        updater.connect()

        new_bio = updater.update_bio("https://example.com/screenshot.png", prepend=True)

        # New compact format
        assert "![Profile]" in new_bio
        assert "Existing bio" in new_bio
        assert new_bio.index("![Profile]") < new_bio.index("Existing bio")
        mock_user.edit.assert_called_once()

    @patch("src.bio_updater.Github")
    def test_update_bio_append(self, mock_github):
        """Test updating bio with append mode."""
        mock_user = MagicMock()
        mock_user.login = "testuser"
        mock_user.bio = "Existing bio"

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        updater = BioUpdater("test_token", "testuser")
        updater.connect()

        new_bio = updater.update_bio("https://example.com/screenshot.png", prepend=False)

        # New compact format
        assert "![Profile]" in new_bio
        assert "Existing bio" in new_bio
        assert new_bio.index("Existing bio") < new_bio.index("![Profile]")

    @patch("src.bio_updater.Github")
    def test_update_bio_removes_existing_screenshot(self, mock_github):
        """Test that existing screenshot links are removed."""
        existing_bio = """<!-- github-screenshot-automation -->
![Profile Screenshot](https://example.com/old.png)

Other bio content"""

        mock_user = MagicMock()
        mock_user.login = "testuser"
        mock_user.bio = existing_bio

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        updater = BioUpdater("test_token", "testuser")
        updater.connect()

        new_bio = updater.update_bio("https://example.com/new.png")

        # Old screenshot should be removed
        assert "old.png" not in new_bio
        # New screenshot should be present
        assert "new.png" in new_bio
        # Other content should remain
        assert "Other bio content" in new_bio

    @patch("src.bio_updater.Github")
    def test_update_bio_length_limit(self, mock_github):
        """Test bio truncation when exceeding length limit."""
        long_bio = "A" * 200  # Exceeds 160 character limit

        mock_user = MagicMock()
        mock_user.login = "testuser"
        mock_user.bio = long_bio

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        updater = BioUpdater("test_token", "testuser")
        updater.connect()

        new_bio = updater.update_bio("https://example.com/screenshot.png")

        # Bio should be truncated
        assert len(new_bio) <= 160
        # Screenshot link should still be present
        assert "screenshot.png" in new_bio

    def test_format_screenshot_link(self):
        """Test screenshot link formatting."""
        updater = BioUpdater("test_token", "testuser")
        link = updater._format_screenshot_link("https://example.com/test.png")

        # New compact format for bio length constraints
        assert "![Profile]" in link
        assert "https://example.com/test.png" in link
        # Should not contain old long format
        assert "Profile Screenshot" not in link
        assert "<!--" not in link

    def test_remove_existing_screenshot_links(self):
        """Test removal of existing screenshot links."""
        bio_with_screenshot = """<!-- github-screenshot-automation -->
![Profile Screenshot](https://example.com/screenshot.png)

Other content here"""

        updater = BioUpdater("test_token", "testuser")
        cleaned = updater._remove_existing_screenshot_links(bio_with_screenshot)

        assert "<!-- github-screenshot-automation -->" not in cleaned
        assert "![Profile Screenshot]" not in cleaned
        assert "Other content here" in cleaned

    @patch("src.bio_updater.Github")
    def test_rollback_success(self, mock_github):
        """Test successful bio rollback."""
        mock_user = MagicMock()
        mock_user.login = "testuser"
        mock_user.bio = "Original bio"

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        updater = BioUpdater("test_token", "testuser")
        updater.connect()
        updater.get_current_bio()

        # Change bio
        updater.original_bio = "Original bio"

        # Rollback
        updater.rollback()

        mock_user.edit.assert_called_once_with(bio="Original bio")

    def test_rollback_no_original_bio(self):
        """Test rollback without original bio stored."""
        updater = BioUpdater("test_token", "testuser")

        with pytest.raises(ValueError) as excinfo:
            updater.rollback()

        assert "No original bio stored" in str(excinfo.value)

    @patch("src.bio_updater.BioUpdater")
    def test_update_github_bio_function(self, mock_updater_class):
        """Test convenience function for bio update."""
        mock_instance = MagicMock()
        mock_instance.update_bio.return_value = "New bio"
        mock_updater_class.return_value = mock_instance

        result = update_github_bio("token", "testuser", "https://example.com/screenshot.png")

        assert result == "New bio"
        mock_instance.update_bio.assert_called_once()
        mock_instance.close.assert_called_once()
