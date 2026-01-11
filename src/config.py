"""Configuration management for the GitHub screenshot automation system."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration container for application settings."""

    # GitHub Authentication (required)
    github_token: str
    github_username: str

    # Target Profile (required)
    profile_url: str

    # Profile Repository (hardcoded)
    profile_repo: str = "fUmar3542/fUmar3542"

    # GitHub Repository path (optional)
    screenshot_path: str = "screenshots"

    # Screenshot Settings (optional)
    viewport_width: int = 1920
    viewport_height: int = 1080
    screenshot_quality: int = 90

    # Application Settings (optional)
    dry_run: bool = False
    log_level: str = "INFO"

    # Scheduling (optional)
    schedule_time: str = "00:00"
    timezone: str = "UTC"

    @classmethod
    def from_env(cls, env_file: str | None = None) -> "Config":
        """
        Load configuration from environment variables.

        Args:
            env_file: Optional path to .env file

        Returns:
            Config instance with loaded values

        Raises:
            ValueError: If required environment variables are missing
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        # Required variables
        required_vars = {
            "GITHUB_TOKEN": "GitHub personal access token",
            "GITHUB_USERNAME": "GitHub username",
            "PROFILE_URL": "GitHub profile URL to screenshot",
        }

        missing_vars = []
        for var, description in required_vars.items():
            if not os.getenv(var):
                missing_vars.append(f"{var} ({description})")

        if missing_vars:
            raise ValueError(
                "Missing required environment variables:\n"
                + "\n".join(f"  - {var}" for var in missing_vars)
            )

        # Validate profile URL
        profile_url = os.getenv("PROFILE_URL", "")
        if not profile_url.startswith("https://github.com/"):
            raise ValueError(
                f"PROFILE_URL must start with 'https://github.com/', got: {profile_url}"
            )

        return cls(
            github_token=os.getenv("GITHUB_TOKEN", ""),
            github_username=os.getenv("GITHUB_USERNAME", ""),
            profile_url=profile_url,
            screenshot_path=os.getenv("SCREENSHOT_PATH", "screenshots"),
            viewport_width=int(os.getenv("VIEWPORT_WIDTH", "1920")),
            viewport_height=int(os.getenv("VIEWPORT_HEIGHT", "1080")),
            screenshot_quality=int(os.getenv("SCREENSHOT_QUALITY", "90")),
            dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            schedule_time=os.getenv("SCHEDULE_TIME", "00:00"),
            timezone=os.getenv("TIMEZONE", "UTC"),
        )

    def validate(self) -> None:
        """
        Validate configuration values.

        Raises:
            ValueError: If any configuration value is invalid
        """
        if self.viewport_width < 800 or self.viewport_width > 3840:
            raise ValueError(f"Invalid viewport width: {self.viewport_width}")

        if self.viewport_height < 600 or self.viewport_height > 2160:
            raise ValueError(f"Invalid viewport height: {self.viewport_height}")

        if self.screenshot_quality < 1 or self.screenshot_quality > 100:
            raise ValueError(f"Invalid screenshot quality: {self.screenshot_quality}")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {self.log_level}")


def load_config(env_file: str | None = None) -> Config:
    """
    Load and validate configuration.

    Args:
        env_file: Optional path to .env file

    Returns:
        Validated Config instance
    """
    config = Config.from_env(env_file)
    config.validate()
    return config
