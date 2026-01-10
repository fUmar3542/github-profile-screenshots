"""GitHub profile bio updater module."""

import logging
import re

from github import Github, GithubException

logger = logging.getLogger("github_screenshot_automation.bio")


class BioUpdater:
    """Handles updating GitHub profile bio with screenshot links."""

    # Use shorter marker for bio length constraints
    SCREENSHOT_MARKER = "![Profile]"

    def __init__(self, token: str, username: str):
        """
        Initialize bio updater.

        Args:
            token: GitHub personal access token
            username: GitHub username to update bio for
        """
        self.token = token
        self.username = username
        self.github: Github | None = None
        self.original_bio: str | None = None

    def connect(self) -> None:
        """
        Connect to GitHub API.

        Raises:
            Exception: If connection or authentication fails
        """
        try:
            logger.info("Connecting to GitHub API for bio update")
            self.github = Github(self.token)

            # Test authentication
            user = self.github.get_user()
            logger.info(f"Authenticated as: {user.login}")

            if user.login != self.username:
                logger.warning(
                    f"Authenticated user ({user.login}) differs from target user ({self.username})"
                )

        except GithubException as e:
            logger.error(f"GitHub API error: {e.status} - {e.data}")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to GitHub: {e}")
            raise

    def get_current_bio(self) -> str:
        """
        Fetch current bio content.

        Returns:
            Current bio text

        Raises:
            Exception: If fetching bio fails
        """
        if not self.github:
            self.connect()

        try:
            user = self.github.get_user()
            bio = user.bio or ""
            logger.info(f"Current bio length: {len(bio)} characters")
            self.original_bio = bio
            return bio

        except GithubException as e:
            logger.error(f"Failed to fetch bio: {e.status} - {e.data}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch bio: {e}")
            raise

    def update_bio(self, screenshot_url: str, prepend: bool = True) -> str:
        """
        Update bio with screenshot link.

        Args:
            screenshot_url: Raw URL to screenshot
            prepend: If True, add link at beginning; if False, replace existing link

        Returns:
            New bio content

        Raises:
            Exception: If bio update fails
        """
        if not self.github:
            self.connect()

        try:
            # Get current bio
            current_bio = self.get_current_bio()

            # Generate screenshot link markdown
            screenshot_link = self._format_screenshot_link(screenshot_url)

            # Remove existing screenshot links
            new_bio = self._remove_existing_screenshot_links(current_bio)

            # Add new screenshot link
            if prepend:
                if new_bio:
                    new_bio = f"{screenshot_link}\n\n{new_bio}"
                else:
                    new_bio = screenshot_link
            else:
                if new_bio:
                    new_bio = f"{new_bio}\n\n{screenshot_link}"
                else:
                    new_bio = screenshot_link

            # Validate bio length (GitHub limit is 160 characters)
            if len(new_bio) > 160:
                logger.warning(
                    f"Bio length ({len(new_bio)}) exceeds GitHub limit (160). Truncating..."
                )
                # Try to keep screenshot link and truncate other content
                if prepend:
                    available_space = 160 - len(screenshot_link) - 2  # -2 for newlines
                    truncated = current_bio[:available_space].rstrip()
                    new_bio = f"{screenshot_link}\n\n{truncated}" if truncated else screenshot_link
                else:
                    new_bio = screenshot_link

            # Update bio
            logger.info(f"Updating bio (new length: {len(new_bio)} characters)")
            user = self.github.get_user()
            user.edit(bio=new_bio)

            logger.info("Bio updated successfully")
            return new_bio

        except GithubException as e:
            logger.error(f"Failed to update bio: {e.status} - {e.data}")
            raise
        except Exception as e:
            logger.error(f"Failed to update bio: {e}")
            raise

    def _format_screenshot_link(self, screenshot_url: str) -> str:
        """
        Format screenshot URL as markdown link (optimized for bio length).

        Args:
            screenshot_url: Raw URL to screenshot

        Returns:
            Formatted markdown link (compact format to fit 160 char limit)
        """
        # Use compact format: ![Profile](URL) - no HTML comments, shorter alt text
        return f"![Profile]({screenshot_url})"

    def _remove_existing_screenshot_links(self, bio: str) -> str:
        """
        Remove existing screenshot links from bio.

        Args:
            bio: Current bio content

        Returns:
            Bio with screenshot links removed
        """
        # Remove old format with HTML comment marker
        pattern = r"<!-- github-screenshot-automation -->\s*\n?\s*!\[.*?\]\(.*?\)"
        cleaned = re.sub(pattern, "", bio, flags=re.MULTILINE)

        # Remove new compact format: ![Profile](URL)
        pattern = r"!\[Profile\]\(https://raw\.githubusercontent\.com/[^\)]+\)"
        cleaned = re.sub(pattern, "", cleaned)

        # Also remove old format standalone image links
        pattern = r"!\[Profile Screenshot\]\(.*?\)"
        cleaned = re.sub(pattern, "", cleaned)

        # Clean up extra whitespace
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = cleaned.strip()

        return cleaned

    def rollback(self) -> None:
        """
        Rollback bio to original content.

        Raises:
            Exception: If rollback fails or no original bio is stored
        """
        if self.original_bio is None:
            raise ValueError("No original bio stored for rollback")

        if not self.github:
            self.connect()

        try:
            logger.info("Rolling back bio to original content")
            user = self.github.get_user()
            user.edit(bio=self.original_bio)
            logger.info("Bio rollback successful")

        except GithubException as e:
            logger.error(f"Failed to rollback bio: {e.status} - {e.data}")
            raise
        except Exception as e:
            logger.error(f"Failed to rollback bio: {e}")
            raise

    def close(self) -> None:
        """Close GitHub connection."""
        if self.github:
            self.github.close()
            logger.debug("GitHub connection closed")


def update_github_bio(token: str, username: str, screenshot_url: str) -> str:
    """
    Convenience function to update GitHub bio with screenshot link.

    Args:
        token: GitHub personal access token
        username: GitHub username
        screenshot_url: Raw URL to screenshot

    Returns:
        New bio content
    """
    updater = BioUpdater(token, username)
    try:
        return updater.update_bio(screenshot_url)
    finally:
        updater.close()
