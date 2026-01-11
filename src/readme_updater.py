"""GitHub profile README updater module."""

import logging
from datetime import datetime

from github import Github, GithubException

logger = logging.getLogger("github_screenshot_automation.readme")


class ReadmeUpdater:
    """Handles updating GitHub profile README with screenshot images."""

    # Marker for identifying screenshot sections in README
    SCREENSHOT_MARKER = "![Profile Screenshot]"
    # Hardcoded profile repository
    PROFILE_REPO = "fUmar3542/fUmar3542"

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
        self.repo_name = self.PROFILE_REPO

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
            return content

        except GithubException as e:
            if e.status == 404:
                logger.warning(f"README.md not found in {self.repo_name}. Will create new one.")
                return ""
            logger.error(f"Failed to fetch README: {e.status} - {e.data}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch README: {e}")
            raise

    def update_readme(self, screenshot_filename: str) -> str:
        """
        Update README with screenshot image using relative path.

        Args:
            screenshot_filename: Screenshot filename (e.g., '2026-01-10.png')

        Returns:
            New README content

        Raises:
            Exception: If README update fails
        """
        if not self.github:
            self.connect()

        try:
            # Generate screenshot markdown image with relative path
            screenshot_image = self._format_screenshot_link(screenshot_filename)

            # README will only contain the screenshot image
            new_readme = screenshot_image

            # Update README in repository
            logger.info(f"Updating README.md in {self.repo_name} with relative path")

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

    def _format_screenshot_link(self, screenshot_filename: str) -> str:
        """
        Format screenshot filename as markdown image with relative path.

        Args:
            screenshot_filename: Screenshot filename (e.g., '2026-01-10.png')

        Returns:
            Formatted markdown image with relative path
        """
        # Use relative path format: ./screenshots/filename
        relative_path = f"./screenshots/{screenshot_filename}"
        return f"![Profile Screenshot]({relative_path})"

    def close(self) -> None:
        """Close GitHub connection."""
        if self.github:
            self.github.close()
            logger.debug("GitHub connection closed")


def update_github_readme(token: str, username: str, screenshot_filename: str) -> str:
    """
    Convenience function to update GitHub profile README with screenshot image.

    Args:
        token: GitHub personal access token
        username: GitHub username
        screenshot_filename: Screenshot filename

    Returns:
        New README content
    """
    updater = ReadmeUpdater(token, username)
    try:
        return updater.update_readme(screenshot_filename)
    finally:
        updater.close()
