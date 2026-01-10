"""Unit tests for configuration module."""

import os
from unittest.mock import patch

import pytest

from src.config import Config


class TestConfig:
    """Test cases for Config class."""

    @patch.dict(
        os.environ,
        {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_USERNAME": "testuser",
            "GITHUB_REPO": "testuser/test-repo",
            "PROFILE_URL": "https://github.com/testuser",
        },
    )
    def test_from_env_with_required_vars(self):
        """Test loading configuration with all required variables."""
        config = Config.from_env()
        assert config.github_token == "test_token"
        assert config.github_username == "testuser"
        assert config.github_repo == "testuser/test-repo"
        assert config.profile_url == "https://github.com/testuser"

    @patch("src.config.load_dotenv")
    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_missing_required_vars(self, mock_load_dotenv):
        """Test that missing required variables raise ValueError."""
        mock_load_dotenv.return_value = None
        with pytest.raises(ValueError) as excinfo:
            Config.from_env()
        assert "Missing required environment variables" in str(excinfo.value)

    @patch.dict(
        os.environ,
        {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_USERNAME": "testuser",
            "GITHUB_REPO": "invalid_format",
            "PROFILE_URL": "https://github.com/testuser",
        },
    )
    def test_from_env_invalid_repo_format(self):
        """Test that invalid repository format raises ValueError."""
        with pytest.raises(ValueError) as excinfo:
            Config.from_env()
        assert "must be in format 'owner/repo'" in str(excinfo.value)

    @patch.dict(
        os.environ,
        {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_USERNAME": "testuser",
            "GITHUB_REPO": "testuser/test-repo",
            "PROFILE_URL": "https://example.com/testuser",
        },
    )
    def test_from_env_invalid_profile_url(self):
        """Test that invalid profile URL raises ValueError."""
        with pytest.raises(ValueError) as excinfo:
            Config.from_env()
        assert "must start with 'https://github.com/'" in str(excinfo.value)

    @patch.dict(
        os.environ,
        {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_USERNAME": "testuser",
            "GITHUB_REPO": "testuser/test-repo",
            "PROFILE_URL": "https://github.com/testuser",
            "VIEWPORT_WIDTH": "2560",
            "VIEWPORT_HEIGHT": "1440",
            "SCREENSHOT_QUALITY": "95",
            "DRY_RUN": "true",
            "LOG_LEVEL": "DEBUG",
        },
    )
    def test_from_env_with_optional_vars(self):
        """Test loading configuration with optional variables."""
        config = Config.from_env()
        assert config.viewport_width == 2560
        assert config.viewport_height == 1440
        assert config.screenshot_quality == 95
        assert config.dry_run is True
        assert config.log_level == "DEBUG"

    def test_validate_valid_config(self):
        """Test validation with valid configuration."""
        config = Config(
            github_token="test",
            github_username="test",
            github_repo="test/repo",
            profile_url="https://github.com/test",
        )
        config.validate()  # Should not raise

    def test_validate_invalid_viewport_width(self):
        """Test validation with invalid viewport width."""
        config = Config(
            github_token="test",
            github_username="test",
            github_repo="test/repo",
            profile_url="https://github.com/test",
            viewport_width=500,
        )
        with pytest.raises(ValueError) as excinfo:
            config.validate()
        assert "Invalid viewport width" in str(excinfo.value)

    def test_validate_invalid_viewport_height(self):
        """Test validation with invalid viewport height."""
        config = Config(
            github_token="test",
            github_username="test",
            github_repo="test/repo",
            profile_url="https://github.com/test",
            viewport_height=400,
        )
        with pytest.raises(ValueError) as excinfo:
            config.validate()
        assert "Invalid viewport height" in str(excinfo.value)

    def test_validate_invalid_quality(self):
        """Test validation with invalid screenshot quality."""
        config = Config(
            github_token="test",
            github_username="test",
            github_repo="test/repo",
            profile_url="https://github.com/test",
            screenshot_quality=150,
        )
        with pytest.raises(ValueError) as excinfo:
            config.validate()
        assert "Invalid screenshot quality" in str(excinfo.value)

    def test_validate_invalid_log_level(self):
        """Test validation with invalid log level."""
        config = Config(
            github_token="test",
            github_username="test",
            github_repo="test/repo",
            profile_url="https://github.com/test",
            log_level="INVALID",
        )
        with pytest.raises(ValueError) as excinfo:
            config.validate()
        assert "Invalid log level" in str(excinfo.value)
