"""Main orchestration script for GitHub screenshot automation."""

import argparse
import sys

from .bio_updater import BioUpdater
from .config import load_config
from .github_uploader import GitHubUploader
from .screenshot_capture import ScreenshotCapture
from .utils import (
    cleanup_old_screenshots,
    generate_screenshot_filename,
    get_project_root,
    setup_logging,
)

logger = None


def run_workflow(dry_run: bool = False) -> None:
    """
    Execute the complete screenshot automation workflow.

    Args:
        dry_run: If True, skip actual API calls

    Raises:
        Exception: If any step of the workflow fails
    """
    global logger

    try:
        # Load configuration
        config = load_config()

        # Initialize logging
        logger = setup_logging(config.log_level)
        logger.info("Starting GitHub screenshot automation workflow")
        logger.info(f"Dry run mode: {dry_run or config.dry_run}")

        # Step 1: Capture screenshot
        logger.info("=" * 60)
        logger.info("Step 1: Capturing screenshot")
        logger.info("=" * 60)

        screenshots_dir = get_project_root() / "screenshots"
        screenshot_filename = generate_screenshot_filename()
        screenshot_path = screenshots_dir / screenshot_filename

        capturer = ScreenshotCapture(
            viewport_width=config.viewport_width,
            viewport_height=config.viewport_height,
            quality=config.screenshot_quality,
        )

        screenshot_path = capturer.capture_sync(config.profile_url, screenshot_path)
        logger.info(f"Screenshot captured: {screenshot_path}")

        if dry_run or config.dry_run:
            logger.info("DRY RUN: Skipping upload and bio update")
            logger.info(f"Screenshot saved at: {screenshot_path}")
            return

        # Step 2: Upload to GitHub
        logger.info("=" * 60)
        logger.info("Step 2: Uploading to GitHub repository")
        logger.info("=" * 60)

        uploader = GitHubUploader(config.github_token, config.github_repo)
        remote_path = f"{config.screenshot_path}/{screenshot_filename}"

        try:
            raw_url = uploader.upload_screenshot(
                file_path=screenshot_path,
                remote_path=remote_path,
                commit_message=f"Add profile screenshot: {screenshot_filename}",
            )
            logger.info(f"Screenshot uploaded. Raw URL: {raw_url}")
        finally:
            uploader.close()

        # Step 3: Update bio
        logger.info("=" * 60)
        logger.info("Step 3: Updating GitHub profile bio")
        logger.info("=" * 60)

        bio_updater = BioUpdater(config.github_token, config.github_username)

        try:
            new_bio = bio_updater.update_bio(raw_url, prepend=True)
            logger.info("Bio updated successfully")
            logger.info(f"New bio: {new_bio}")
        except Exception as e:
            logger.error(f"Failed to update bio: {e}")
            logger.info("Attempting rollback...")
            try:
                bio_updater.rollback()
                logger.info("Rollback successful")
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}")
            raise
        finally:
            bio_updater.close()

        # Step 4: Cleanup old screenshots
        logger.info("=" * 60)
        logger.info("Step 4: Cleaning up old screenshots")
        logger.info("=" * 60)

        cleanup_old_screenshots(screenshots_dir, keep_count=30)
        logger.info("Cleanup completed")

        logger.info("=" * 60)
        logger.info("Workflow completed successfully!")
        logger.info("=" * 60)

    except Exception as e:
        if logger:
            logger.error(f"Workflow failed: {e}")
        raise


def main() -> int:
    """
    Main entry point for the application.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    global logger

    parser = argparse.ArgumentParser(
        description="GitHub Profile Screenshot Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default configuration
  python -m src.main

  # Run in dry-run mode (no API calls)
  python -m src.main --dry-run

  # Specify custom environment file
  python -m src.main --env-file .env.production

  # Set custom log level
  python -m src.main --log-level DEBUG
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making API calls (for testing)",
    )

    parser.add_argument(
        "--env-file",
        type=str,
        help="Path to environment file (default: .env)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (overrides config)",
    )

    args = parser.parse_args()

    # Initialize basic logging for startup
    logger = setup_logging(args.log_level or "INFO")

    try:
        run_workflow(dry_run=args.dry_run)
        return 0
    except KeyboardInterrupt:
        logger.info("\nWorkflow interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
