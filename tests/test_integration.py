"""Integration tests for the complete workflow."""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.main import run_workflow


class TestIntegration:
    """Integration test cases for end-to-end workflow."""

    @patch.dict(
        os.environ,
        {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_USERNAME": "testuser",
            "PROFILE_URL": "https://github.com/testuser",
            "DRY_RUN": "true",
        },
    )
    @patch("src.main.ScreenshotCapture")
    @patch("src.main.setup_logging")
    def test_workflow_dry_run(self, mock_logging, mock_capturer_class, tmp_path):
        """Test complete workflow in dry-run mode."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_logging.return_value = mock_logger

        mock_capturer = MagicMock()
        screenshot_path = tmp_path / "screenshots" / "test_screenshot.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_path.touch()
        mock_capturer.capture_sync.return_value = screenshot_path
        mock_capturer_class.return_value = mock_capturer

        # Run workflow
        with patch("src.main.get_project_root", return_value=tmp_path):
            run_workflow(dry_run=True)

        # Assertions
        mock_capturer.capture_sync.assert_called_once()
        # In dry-run, upload and README update should not be called

    @patch.dict(
        os.environ,
        {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_USERNAME": "testuser",
            "PROFILE_URL": "https://github.com/testuser",
            "DRY_RUN": "false",
        },
    )
    @patch("src.main.cleanup_old_screenshots")
    @patch("src.main.ReadmeUpdater")
    @patch("src.main.GitHubUploader")
    @patch("src.main.ScreenshotCapture")
    @patch("src.main.setup_logging")
    def test_workflow_full_success(
        self,
        mock_logging,
        mock_capturer_class,
        mock_uploader_class,
        mock_readme_updater_class,
        mock_cleanup,
        tmp_path,
    ):
        """Test complete workflow with all steps."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_logging.return_value = mock_logger

        # Screenshot capture
        mock_capturer = MagicMock()
        screenshot_path = tmp_path / "screenshots" / "test_screenshot.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_path.touch()
        mock_capturer.capture_sync.return_value = screenshot_path
        mock_capturer_class.return_value = mock_capturer

        # GitHub uploader
        mock_uploader = MagicMock()
        mock_uploader.upload_screenshot.return_value = "./screenshots/test_screenshot.png"
        mock_uploader_class.return_value = mock_uploader

        # README updater
        mock_readme_updater = MagicMock()
        mock_readme_updater.update_readme.return_value = "![Profile Screenshot](./screenshots/test_screenshot.png)"
        mock_readme_updater_class.return_value = mock_readme_updater

        # Run workflow
        with patch("src.main.get_project_root", return_value=tmp_path):
            run_workflow(dry_run=False)

        # Assertions
        mock_capturer.capture_sync.assert_called_once()
        mock_uploader.upload_screenshot.assert_called_once()
        mock_readme_updater.update_readme.assert_called_once()
        mock_cleanup.assert_called_once()

    @patch.dict(
        os.environ,
        {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_USERNAME": "testuser",
            "PROFILE_URL": "https://github.com/testuser",
            "DRY_RUN": "false",
        },
    )
    @patch("src.main.ReadmeUpdater")
    @patch("src.main.GitHubUploader")
    @patch("src.main.ScreenshotCapture")
    @patch("src.main.setup_logging")
    def test_workflow_screenshot_failure(
        self,
        mock_logging,
        mock_capturer_class,
        mock_uploader_class,
        mock_readme_updater_class,
        tmp_path,
    ):
        """Test workflow when screenshot capture fails."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_logging.return_value = mock_logger

        # Screenshot capture fails
        mock_capturer = MagicMock()
        mock_capturer.capture_sync.side_effect = Exception("Screenshot failed")
        mock_capturer_class.return_value = mock_capturer

        # Run workflow should raise exception
        with patch("src.main.get_project_root", return_value=tmp_path):
            with pytest.raises(Exception) as excinfo:
                run_workflow(dry_run=False)

        assert "Screenshot failed" in str(excinfo.value)

        # Upload and README update should not be called
        mock_uploader = mock_uploader_class.return_value
        mock_uploader.upload_screenshot.assert_not_called()

    @patch.dict(
        os.environ,
        {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_USERNAME": "testuser",
            "PROFILE_URL": "https://github.com/testuser",
            "DRY_RUN": "false",
        },
    )
    @patch("src.main.ReadmeUpdater")
    @patch("src.main.GitHubUploader")
    @patch("src.main.ScreenshotCapture")
    @patch("src.main.setup_logging")
    def test_workflow_upload_failure(
        self,
        mock_logging,
        mock_capturer_class,
        mock_uploader_class,
        mock_readme_updater_class,
        tmp_path,
    ):
        """Test workflow when upload fails."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_logging.return_value = mock_logger

        # Screenshot capture succeeds
        mock_capturer = MagicMock()
        screenshot_path = tmp_path / "screenshots" / "test_screenshot.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_path.touch()
        mock_capturer.capture_sync.return_value = screenshot_path
        mock_capturer_class.return_value = mock_capturer

        # Upload fails
        mock_uploader = MagicMock()
        mock_uploader.upload_screenshot.side_effect = Exception("Upload failed")
        mock_uploader_class.return_value = mock_uploader

        # Run workflow should raise exception
        with patch("src.main.get_project_root", return_value=tmp_path):
            with pytest.raises(Exception) as excinfo:
                run_workflow(dry_run=False)

        assert "Upload failed" in str(excinfo.value)

        # README update should not be called
        mock_readme_updater = mock_readme_updater_class.return_value
        mock_readme_updater.update_readme.assert_not_called()

    @patch.dict(
        os.environ,
        {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_USERNAME": "testuser",
            "PROFILE_URL": "https://github.com/testuser",
            "DRY_RUN": "false",
        },
    )
    @patch("src.main.cleanup_old_screenshots")
    @patch("src.main.ReadmeUpdater")
    @patch("src.main.GitHubUploader")
    @patch("src.main.ScreenshotCapture")
    @patch("src.main.setup_logging")
    def test_workflow_readme_update_failure(
        self,
        mock_logging,
        mock_capturer_class,
        mock_uploader_class,
        mock_readme_updater_class,
        mock_cleanup,
        tmp_path,
    ):
        """Test workflow when README update fails."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_logging.return_value = mock_logger

        # Screenshot capture succeeds
        mock_capturer = MagicMock()
        screenshot_path = tmp_path / "screenshots" / "test_screenshot.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_path.touch()
        mock_capturer.capture_sync.return_value = screenshot_path
        mock_capturer_class.return_value = mock_capturer

        # Upload succeeds
        mock_uploader = MagicMock()
        mock_uploader.upload_screenshot.return_value = "./screenshots/test.png"
        mock_uploader_class.return_value = mock_uploader

        # README update fails
        mock_readme_updater = MagicMock()
        mock_readme_updater.update_readme.side_effect = Exception("README update failed")
        mock_readme_updater_class.return_value = mock_readme_updater

        # Run workflow should raise exception
        with patch("src.main.get_project_root", return_value=tmp_path):
            with pytest.raises(Exception) as excinfo:
                run_workflow(dry_run=False)

        assert "README update failed" in str(excinfo.value)

    @patch.dict(
        os.environ,
        {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_USERNAME": "testuser",
            "PROFILE_URL": "https://github.com/testuser",
        },
    )
    def test_workflow_missing_env_vars(self):
        """Test workflow with missing environment variables."""
        # Clear required env var
        with patch.dict(os.environ, {"GITHUB_TOKEN": ""}, clear=False):
            with pytest.raises(ValueError) as excinfo:
                run_workflow()

        assert "Missing required environment variables" in str(excinfo.value)
