"""GitHub profile README updater module."""

import logging
import re
from datetime import datetime

from github import Github, GithubException

logger = logging.getLogger("github_screenshot_automation.readme")


class BioUpdater:
    """Handles updating GitHub profile README with screenshot images."""

    # Marker for identifying screenshot sections in README
    SCREENSHOT_MARKER = "![Profile Screenshot]"

    def __init__(self, token: str, username: str):
        """
        Initialize README updater.

        Args:
            token: GitHub personal access token
            username: GitHub username (repository owner)
        """
        self.token = token
        self.username = username
        self.github: Github | None = None
        self.original_readme: str | None = None
        self.repo_name = f"{username}/{username}"  # Profile repository

    def connect(self) -> None:
        """
        Connect to GitHub API.

        Raises:
            Exception: If connection or authentication fails
        """
        try:
            logger.info("Connecting to GitHub API for README update")
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

    def get_current_readme(self) -> str:
        """
        Fetch current README content.

        Returns:
            Current README text

        Raises:
            Exception: If fetching README fails
        """
        if not self.github:
            self.connect()

        try:
            repo = self.github.get_repo(self.repo_name)
            readme = repo.get_readme()
            content = readme.decoded_content.decode('utf-8')
            logger.info(f"Current README length: {len(content)} characters")
            self.original_readme = content
            return content

        except GithubException as e:
            if e.status == 404:
                logger.warning(f"README.md not found in {self.repo_name}. Will create new one.")
                self.original_readme = ""
                return ""
            logger.error(f"Failed to fetch README: {e.status} - {e.data}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch README: {e}")
            raise

    def update_bio(self, screenshot_url: str, prepend: bool = True) -> str:
        """
        Update README with screenshot image only.

        Args:
            screenshot_url: Raw URL to screenshot
            prepend: If True, add image at beginning; if False, at end (ignored, kept for compatibility)

        Returns:
            New README content (only the screenshot)

        Raises:
            Exception: If README update fails
        """
        if not self.github:
            self.connect()

        try:
            # Generate screenshot markdown image
            screenshot_image = self._format_screenshot_link(screenshot_url)

            # README will only contain the screenshot image
            new_readme = screenshot_image

            # Update README in repository
            logger.info(f"Updating README.md in {self.repo_name} (new length: {len(new_readme)} characters)")

            try:
                repo = self.github.get_repo(self.repo_name)
            except GithubException as e:
                if e.status == 404:
                    # Repository doesn't exist, create it
                    logger.warning(f"Repository {self.repo_name} not found. Creating it...")
                    user = self.github.get_user()
                    repo = user.create_repo(
                        name=self.username,
                        description=f"GitHub profile for {self.username}",
                        private=False,
                        auto_init=False
                    )
                    logger.info(f"Repository {self.repo_name} created successfully")
                else:
                    raise

            try:
                # Try to get existing README
                readme_file = repo.get_readme()
                commit_message = f"Update profile screenshot - {datetime.now().strftime('%Y-%m-%d')}"
                repo.update_file(
                    path="README.md",
                    message=commit_message,
                    content=new_readme,
                    sha=readme_file.sha,
                    branch="main"
                )
                logger.info(f"README.md updated successfully with commit: {commit_message}")
            except GithubException as e:
                if e.status == 404:
                    # README doesn't exist, create it
                    commit_message = f"Create README with profile screenshot - {datetime.now().strftime('%Y-%m-%d')}"
                    repo.create_file(
                        path="README.md",
                        message=commit_message,
                        content=new_readme,
                        branch="main"
                    )
                    logger.info(f"README.md created successfully with commit: {commit_message}")
                else:
                    raise

            return new_readme

        except GithubException as e:
            logger.error(f"Failed to update README: {e.status} - {e.data}")
            raise
        except Exception as e:
            logger.error(f"Failed to update README: {e}")
            raise

    def _format_screenshot_link(self, screenshot_url: str) -> str:
        """
        Format screenshot URL as markdown image.

        Args:
            screenshot_url: Raw URL to screenshot

        Returns:
            Formatted markdown image that displays the screenshot
        """
        # Use markdown image syntax to embed the actual image
        return f"![Profile Screenshot]({screenshot_url})"

    def _remove_existing_screenshot_links(self, readme: str) -> str:
        """
        Remove existing screenshot images from README.

        Args:
            readme: Current README content

        Returns:
            README with screenshot images removed
        """
        # Remove old format with HTML comment marker
        pattern = r"<!-- github-screenshot-automation -->\s*\n?\s*!\[.*?\]\(.*?\)"
        cleaned = re.sub(pattern, "", readme, flags=re.MULTILINE)

        # Remove compact format: ![Profile](URL)
        pattern = r"!\[Profile\]\(https://raw\.githubusercontent\.com/[^\)]+\)"
        cleaned = re.sub(pattern, "", cleaned)

        # Remove main screenshot format: ![Profile Screenshot](URL)
        pattern = r"!\[Profile Screenshot\]\(.*?\)"
        cleaned = re.sub(pattern, "", cleaned)

        # Clean up extra whitespace
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = cleaned.strip()

        return cleaned

    def rollback(self) -> None:
        """
        Rollback README to original content.

        Raises:
            Exception: If rollback fails or no original README is stored
        """
        if self.original_readme is None:
            raise ValueError("No original README stored for rollback")

        if not self.github:
            self.connect()

        try:
            logger.info("Rolling back README to original content")
            repo = self.github.get_repo(self.repo_name)
            readme_file = repo.get_readme()
            commit_message = "Rollback README to original content"
            repo.update_file(
                path="README.md",
                message=commit_message,
                content=self.original_readme,
                sha=readme_file.sha,
                branch="main"
            )
            logger.info("README rollback successful")

        except GithubException as e:
            logger.error(f"Failed to rollback README: {e.status} - {e.data}")
            raise
        except Exception as e:
            logger.error(f"Failed to rollback README: {e}")
            raise

    def close(self) -> None:
        """Close GitHub connection."""
        if self.github:
            self.github.close()
            logger.debug("GitHub connection closed")


def update_github_bio(token: str, username: str, screenshot_url: str) -> str:
    """
    Convenience function to update GitHub profile README with screenshot image.

    Args:
        token: GitHub personal access token
        username: GitHub username
        screenshot_url: Raw URL to screenshot

    Returns:
        New README content
    """
    updater = BioUpdater(token, username)
    try:
        return updater.update_bio(screenshot_url)
    finally:
        updater.close()
