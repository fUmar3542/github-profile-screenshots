"""Unit tests for GitHub uploader module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from github import GithubException

from src.github_uploader import GitHubUploader, upload_to_github


class TestGitHubUploader:
    """Test cases for GitHubUploader class."""

    def test_init(self):
        """Test initialization."""
        uploader = GitHubUploader("test_token", "testuser")
        assert uploader.token == "test_token"
        assert uploader.username == "testuser"
        assert uploader.repo_name == "fUmar3542/fUmar3542"
        assert uploader.max_retries == 3

    @patch("src.github_uploader.Github")
    def test_connect_success(self, mock_github):
        """Test successful GitHub connection."""
        mock_user = MagicMock()
        mock_user.login = "testuser"
        mock_repo = MagicMock()
        mock_repo.full_name = "fUmar3542/fUmar3542"

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        uploader = GitHubUploader("test_token", "testuser")
        uploader.connect()

        assert uploader.github is not None
        assert uploader.repo is not None
        mock_github.assert_called_once_with("test_token")

    @patch("src.github_uploader.Github")
    def test_connect_authentication_failure(self, mock_github):
        """Test connection with authentication failure."""
        mock_github_instance = MagicMock()
        mock_github_instance.get_user.side_effect = GithubException(401, "Unauthorized")
        mock_github.return_value = mock_github_instance

        uploader = GitHubUploader("invalid_token", "testuser")

        with pytest.raises(GithubException):
            uploader.connect()

    @patch("src.github_uploader.Github")
    def test_upload_screenshot_new_file(self, mock_github, tmp_path):
        """Test uploading a new screenshot."""
        # Create test file
        test_file = tmp_path / "test_screenshot.png"
        test_file.write_bytes(b"test image data")

        # Setup mocks
        mock_repo = MagicMock()
        mock_repo.default_branch = "main"
        mock_repo.get_contents.side_effect = GithubException(404, "Not Found")
        mock_repo.create_file.return_value = {"commit": {"sha": "abc123"}}

        mock_user = MagicMock()
        mock_user.login = "testuser"

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        uploader = GitHubUploader("test_token", "testuser")
        uploader.connect()

        # Upload
        relative_path = uploader.upload_screenshot(test_file, "screenshots/test.png", "Test commit")

        # Assertions
        assert relative_path == "./screenshots/test.png"
        mock_repo.create_file.assert_called_once()

    @patch("src.github_uploader.Github")
    def test_upload_screenshot_update_existing(self, mock_github, tmp_path):
        """Test updating an existing screenshot."""
        # Create test file
        test_file = tmp_path / "test_screenshot.png"
        test_file.write_bytes(b"test image data")

        # Setup mocks
        mock_existing = MagicMock()
        mock_existing.sha = "old_sha"

        mock_repo = MagicMock()
        mock_repo.default_branch = "main"
        mock_repo.get_contents.return_value = mock_existing
        mock_repo.update_file.return_value = {"commit": {"sha": "new_sha"}}

        mock_user = MagicMock()
        mock_user.login = "testuser"

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        uploader = GitHubUploader("test_token", "testuser")
        uploader.connect()

        # Upload
        relative_path = uploader.upload_screenshot(test_file, "screenshots/test.png")

        # Assertions
        assert relative_path == "./screenshots/test.png"
        mock_repo.update_file.assert_called_once()

    @patch("src.github_uploader.Github")
    def test_upload_screenshot_file_not_found(self, mock_github):
        """Test upload with non-existent file."""
        mock_github_instance = MagicMock()
        mock_github.return_value = mock_github_instance

        uploader = GitHubUploader("test_token", "testuser")
        uploader.repo = MagicMock()

        with pytest.raises(FileNotFoundError):
            uploader.upload_screenshot(Path("/non/existent/file.png"), "test.png")

    @patch("src.github_uploader.Github")
    @patch("src.github_uploader.time.sleep")
    def test_upload_screenshot_retry_on_failure(self, mock_sleep, mock_github, tmp_path):
        """Test retry logic on upload failure."""
        # Create test file
        test_file = tmp_path / "test_screenshot.png"
        test_file.write_bytes(b"test image data")

        # Setup mocks to fail twice then succeed
        mock_repo = MagicMock()
        mock_repo.default_branch = "main"
        mock_repo.get_contents.side_effect = [
            GithubException(404, "Not Found"),
            GithubException(404, "Not Found"),
            GithubException(404, "Not Found"),
        ]
        mock_repo.create_file.side_effect = [
            GithubException(500, "Server Error"),
            GithubException(500, "Server Error"),
            {"commit": {"sha": "abc123"}},
        ]

        mock_user = MagicMock()
        mock_user.login = "testuser"

        mock_github_instance = MagicMock()
        mock_github_instance.get_user.return_value = mock_user
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        uploader = GitHubUploader("test_token", "testuser", max_retries=3)
        uploader.connect()

        # Upload should succeed after retries
        relative_path = uploader.upload_screenshot(test_file, "screenshots/test.png")

        assert relative_path == "./screenshots/test.png"
        assert mock_sleep.call_count == 2  # Called between retries

    @patch("src.github_uploader.GitHubUploader")
    def test_upload_to_github_function(self, mock_uploader_class, tmp_path):
        """Test convenience function for upload."""
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"test")

        mock_instance = MagicMock()
        mock_instance.upload_screenshot.return_value = "./screenshots/test.png"
        mock_uploader_class.return_value = mock_instance

        result = upload_to_github("token", "testuser", test_file, "screenshots/test.png")

        assert result == "./screenshots/test.png"
        mock_instance.upload_screenshot.assert_called_once()
        mock_instance.close.assert_called_once()
