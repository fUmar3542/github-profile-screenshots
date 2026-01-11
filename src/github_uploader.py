"""GitHub repository uploader module for screenshot storage."""

import logging
import time
from pathlib import Path

from github import Auth, Github, GithubException, Repository

logger = logging.getLogger("github_screenshot_automation.uploader")


class GitHubUploader:
    """Handles uploading screenshots to GitHub profile repository."""

    PROFILE_REPO = "fUmar3542/fUmar3542"

    def __init__(self, token: str, username: str, max_retries: int = 3):
        """
        Initialize GitHub uploader.

        Args:
            token: GitHub personal access token
            username: GitHub username (used for validation)
            max_retries: Maximum number of retry attempts for failed uploads
        """
        self.token = token
        self.username = username
        self.repo_name = self.PROFILE_REPO
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
            auth = Auth.Token(self.token)
            self.github = Github(auth=auth)

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
        Upload screenshot to GitHub profile repository.

        Args:
            file_path: Local path to screenshot file
            remote_path: Remote path in repository (e.g., 'screenshots/screenshot.png')
            commit_message: Optional commit message

        Returns:
            Relative path to uploaded file (e.g., './screenshots/filename.png')

        Raises:
            Exception: If upload fails after all retries
        """
        if not self.repo:
            self.connect()

        if not file_path.exists():
            raise FileNotFoundError(f"Screenshot file not found: {file_path}")

        if commit_message is None:
            commit_message = f"Add screenshot: {file_path.name}"

        logger.info(f"Uploading {file_path} to {self.repo_name}/{remote_path}")

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

                # Return relative path
                relative_path = f"./{remote_path}"
                logger.info(f"Upload successful. Relative path: {relative_path}")
                return relative_path

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

    def close(self) -> None:
        """Close GitHub connection."""
        if self.github:
            self.github.close()
            logger.debug("GitHub connection closed")


def upload_to_github(
    token: str,
    username: str,
    file_path: Path,
    remote_path: str,
    commit_message: str | None = None,
) -> str:
    """
    Convenience function to upload a screenshot to GitHub profile repository.

    Args:
        token: GitHub personal access token
        username: GitHub username
        file_path: Local path to screenshot file
        remote_path: Remote path in repository
        commit_message: Optional commit message

    Returns:
        Relative path to uploaded file
    """
    uploader = GitHubUploader(token, username)
    try:
        return uploader.upload_screenshot(file_path, remote_path, commit_message)
    finally:
        uploader.close()
