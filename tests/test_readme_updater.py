"""Unit tests for README updater module."""

from unittest.mock import MagicMock, patch

import pytest

from src.readme_updater import ReadmeUpdater, update_github_readme


class TestReadmeUpdater:
    """Test cases for ReadmeUpdater class."""

    def test_init(self):
        """Test initialization."""
        updater = ReadmeUpdater("test_token", "testuser")
        assert updater.token == "test_token"
        assert updater.username == "testuser"
        assert updater.github is None
        assert updater.repo_name == "fUmar3542/fUmar3542"

    @patch("src.readme_updater.Github")
    def test_connect_success(self, mock_github):
        """Test successful GitHub connection."""
        mock_user = MagicMock()
        mock_user.login = "testuser"

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        updater = ReadmeUpdater("test_token", "testuser")
        updater.connect()

        assert updater.github is not None
        mock_github.assert_called_once_with("test_token")

    @patch("src.readme_updater.Github")
    def test_get_current_readme(self, mock_github):
        """Test fetching current README."""
        mock_readme = MagicMock()
        mock_readme.decoded_content = b"Current README content"

        mock_repo = MagicMock()
        mock_repo.get_readme.return_value = mock_readme

        mock_user = MagicMock()
        mock_user.login = "testuser"

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        updater = ReadmeUpdater("test_token", "testuser")
        updater.connect()
        readme = updater.get_current_readme()

        assert readme == "Current README content"

    @patch("src.readme_updater.Github")
    def test_update_readme(self, mock_github):
        """Test updating README with screenshot."""
        mock_readme = MagicMock()
        mock_readme.sha = "abc123"

        mock_repo = MagicMock()
        mock_repo.get_readme.return_value = mock_readme
        mock_repo.update_file = MagicMock()

        mock_user = MagicMock()
        mock_user.login = "testuser"

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        updater = ReadmeUpdater("test_token", "testuser")
        updater.connect()

        screenshot_url = "2026-01-10.png"
        new_readme = updater.update_readme(screenshot_url)

        assert "./screenshots/2026-01-10.png" in new_readme
        assert "![Profile Screenshot]" in new_readme
        mock_repo.update_file.assert_called_once()

    def test_format_screenshot_link(self):
        """Test screenshot link formatting with relative path."""
        updater = ReadmeUpdater("test_token", "testuser")
        link = updater._format_screenshot_link("2026-01-10.png")

        assert link == "![Profile Screenshot](./screenshots/2026-01-10.png)"
        assert link.startswith("![Profile Screenshot](./screenshots/")

    def test_profile_repo_constant(self):
        """Test that profile repository is hardcoded."""
        updater = ReadmeUpdater("test_token", "testuser")
        assert updater.PROFILE_REPO == "fUmar3542/fUmar3542"
        assert updater.repo_name == "fUmar3542/fUmar3542"


def test_update_github_readme_convenience_function():
    """Test convenience function for updating README."""
    with patch("src.readme_updater.ReadmeUpdater") as mock_updater_class:
        mock_updater = MagicMock()
        mock_updater.update_readme.return_value = "![Profile Screenshot](./screenshots/test.png)"
        mock_updater_class.return_value = mock_updater

        result = update_github_readme("token", "user", "test.png")

        assert result == "![Profile Screenshot](./screenshots/test.png)"
        mock_updater.update_readme.assert_called_once_with("test.png")
        mock_updater.close.assert_called_once()
