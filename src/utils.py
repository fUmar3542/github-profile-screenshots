"""Utility functions for the GitHub screenshot automation system."""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure and return application logger.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("github_screenshot_automation")
    logger.setLevel(getattr(logging, level))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


def generate_timestamp() -> str:
    """
    Generate timestamp string for file naming.

    Returns:
        Timestamp in format YYYY-MM-DD-HH-MM-SS
    """
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


def generate_screenshot_filename(timestamp: str | None = None) -> str:
    """
    Generate screenshot filename with date only (for shorter URLs).

    Args:
        timestamp: Optional custom timestamp, uses current time if None

    Returns:
        Filename in format YYYY-MM-DD.png (date only, shorter for bio URLs)
    """
    if timestamp is None:
        # Use date only for shorter filenames
        date_str = datetime.now().strftime("%Y-%m-%d")
    else:
        # Extract date from full timestamp if provided
        if len(timestamp) >= 10:
            date_str = timestamp[:10]  # Extract YYYY-MM-DD
        else:
            date_str = timestamp
    return f"{date_str}.png"


def ensure_directory_exists(path: Path) -> None:
    """
    Create directory if it doesn't exist.

    Args:
        path: Directory path to create
    """
    path.mkdir(parents=True, exist_ok=True)


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path to project root
    """
    return Path(__file__).parent.parent


def cleanup_old_screenshots(directory: Path, keep_count: int = 30) -> None:
    """
    Remove old screenshots, keeping only the most recent ones.

    Args:
        directory: Directory containing screenshots
        keep_count: Number of recent screenshots to keep
    """
    if not directory.exists():
        return

    # Find both old format (screenshot-*.png) and new format (YYYY-MM-DD.png)
    screenshots = []
    screenshots.extend(directory.glob("screenshot-*.png"))  # Old format
    screenshots.extend(directory.glob("????-??-??.png"))  # New format (date pattern)

    # Sort by modification time (most recent first)
    screenshots = sorted(
        screenshots,
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )

    # Remove duplicates (in case a file matches both patterns)
    seen = set()
    unique_screenshots = []
    for screenshot in screenshots:
        if screenshot not in seen:
            seen.add(screenshot)
            unique_screenshots.append(screenshot)

    # Delete old screenshots beyond keep_count
    for screenshot in unique_screenshots[keep_count:]:
        screenshot.unlink()
