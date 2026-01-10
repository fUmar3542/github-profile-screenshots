"""GitHub repository uploader module for screenshot storage."""

import logging
import time
from pathlib import Path

from github import Github, GithubException, Repository

logger = logging.getLogger("github_screenshot_automation.uploader")


class GitHubUploader:
    """Handles uploading screenshots to GitHub repository."""

    def __init__(self, token: str, repo_name: str, max_retries: int = 3):
        """
        Initialize GitHub uploader.

        Args:
            token: GitHub personal access token
            repo_name: Repository name in format 'owner/repo'
            max_retries: Maximum number of retry attempts for failed uploads
        """
        self.token = token
        self.repo_name = repo_name
        self.max_retries = max_retries
        self.github: Github | None = None
        self.repo: Repository.Repository | None = None

    def connect(self) -> None:
        """
        Connect to GitHub API and get repository reference.

        Raises:
            Exception: If connection or authentication fails
        """
        try:
            logger.info("Connecting to GitHub API")
            self.github = Github(self.token)

            # Test authentication
            user = self.github.get_user()
            logger.info(f"Authenticated as: {user.login}")

            # Get repository
            logger.info(f"Accessing repository: {self.repo_name}")
            self.repo = self.github.get_repo(self.repo_name)
            logger.info(f"Repository accessed: {self.repo.full_name}")

        except GithubException as e:
            logger.error(f"GitHub API error: {e.status} - {e.data}")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to GitHub: {e}")
            raise

    def upload_screenshot(
        self, file_path: Path, remote_path: str, commit_message: str | None = None
    ) -> str:
        """
        Upload screenshot to GitHub repository.

        Args:
            file_path: Local path to screenshot file
            remote_path: Remote path in repository (e.g., 'screenshots/screenshot.png')
            commit_message: Optional commit message

        Returns:
            Raw URL to uploaded file

        Raises:
            Exception: If upload fails after all retries
        """
        if not self.repo:
            self.connect()

        if not file_path.exists():
            raise FileNotFoundError(f"Screenshot file not found: {file_path}")

        if commit_message is None:
            commit_message = f"Add screenshot: {file_path.name}"

        logger.info(f"Uploading {file_path} to {remote_path}")

        # Read file content
        with open(file_path, "rb") as f:
            content = f.read()

        # Retry logic
        for attempt in range(1, self.max_retries + 1):
            try:
                # Check if file already exists
                try:
                    existing_file = self.repo.get_contents(remote_path)
                    logger.info(f"File exists, updating: {remote_path}")
                    self.repo.update_file(
                        path=remote_path,
                        message=commit_message,
                        content=content,
                        sha=existing_file.sha,
                    )
                except GithubException as e:
                    if e.status == 404:
                        # File doesn't exist, create new
                        logger.info(f"Creating new file: {remote_path}")
                        self.repo.create_file(
                            path=remote_path,
                            message=commit_message,
                            content=content,
                        )
                    else:
                        raise

                # Generate raw URL
                raw_url = self._generate_raw_url(remote_path)
                logger.info(f"Upload successful. Raw URL: {raw_url}")
                return raw_url

            except GithubException as e:
                logger.warning(
                    f"Upload attempt {attempt}/{self.max_retries} failed: {e.status} - {e.data}"
                )
                if attempt < self.max_retries:
                    wait_time = 2**attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("All upload attempts failed")
                    raise

            except Exception as e:
                logger.error(f"Unexpected error during upload: {e}")
                raise

    def _generate_raw_url(self, remote_path: str) -> str:
        """
        Generate raw GitHub URL for file.

        Args:
            remote_path: Remote file path in repository

        Returns:
            Raw URL to access file directly
        """
        # Format: https://raw.githubusercontent.com/owner/repo/main/path/to/file
        owner, repo = self.repo_name.split("/")
        default_branch = self.repo.default_branch if self.repo else "main"
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{remote_path}"
        return raw_url

    def close(self) -> None:
        """Close GitHub connection."""
        if self.github:
            self.github.close()
            logger.debug("GitHub connection closed")


def upload_to_github(
    token: str,
    repo_name: str,
    file_path: Path,
    remote_path: str,
    commit_message: str | None = None,
) -> str:
    """
    Convenience function to upload a screenshot to GitHub.

    Args:
        token: GitHub personal access token
        repo_name: Repository name in format 'owner/repo'
        file_path: Local path to screenshot file
        remote_path: Remote path in repository
        commit_message: Optional commit message

    Returns:
        Raw URL to uploaded file
    """
    uploader = GitHubUploader(token, repo_name)
    try:
        return uploader.upload_screenshot(file_path, remote_path, commit_message)
    finally:
        uploader.close()
