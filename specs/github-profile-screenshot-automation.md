# Feature: GitHub Profile Screenshot Automation

## Feature Description
This feature implements an automated system that runs daily to capture screenshots of a GitHub profile page, upload them to a publicly accessible location, and automatically update the GitHub bio with a link to the latest screenshot. The entire system is containerized using Docker for easy deployment and consistent execution across different environments. The automation uses Playwright for reliable browser automation, GitHub API for bio updates, and GitHub repository storage for screenshot hosting with raw URLs.

## User Story
As a GitHub user
I want to automatically capture and showcase daily screenshots of my GitHub profile
So that I can maintain a visual history of my profile changes and display the latest snapshot in my bio

## Problem Statement
GitHub users often want to track visual changes to their profile over time or showcase their profile appearance externally. Manually capturing screenshots, uploading them, and updating the bio is time-consuming and error-prone. There's no built-in GitHub feature to automate this workflow, requiring users to perform these tasks manually or build custom solutions from scratch.

## Solution Statement
Create a Dockerized Python application that uses Playwright for browser automation to capture high-quality screenshots of the specified GitHub profile. The system will run on a daily schedule (configurable via cron or GitHub Actions), automatically upload screenshots to a designated GitHub repository with timestamped filenames, and use the GitHub API to update the user's bio with a markdown link pointing to the latest screenshot's raw URL. The containerized approach ensures consistent execution regardless of the hosting environment.

## Relevant Files
This is a new project, so all files will be created from scratch:

### New Files

- **Dockerfile** - Defines the Docker container image with Python, Playwright, and browser dependencies
- **docker-compose.yml** - Orchestrates the Docker container with environment variables and scheduling
- **.env.example** - Template for required environment variables (GitHub token, repository details, profile URL)
- **requirements.txt** or **pyproject.toml** - Python dependencies including Playwright, PyGithub, and scheduling libraries
- **src/main.py** - Main entry point that orchestrates the entire workflow
- **src/screenshot_capture.py** - Module containing Playwright logic for capturing profile screenshots
- **src/github_uploader.py** - Module for uploading screenshots to GitHub repository
- **src/bio_updater.py** - Module for updating GitHub bio via API
- **src/config.py** - Configuration management and environment variable loading
- **src/utils.py** - Utility functions for file handling, timestamp generation, etc.
- **tests/test_screenshot_capture.py** - Unit tests for screenshot capture functionality
- **tests/test_github_uploader.py** - Unit tests for GitHub upload functionality
- **tests/test_bio_updater.py** - Unit tests for bio update functionality
- **tests/test_integration.py** - Integration tests for the complete workflow
- **.github/workflows/daily-screenshot.yml** - GitHub Actions workflow for daily execution (optional deployment method)
- **cron-schedule.sh** - Alternative cron-based scheduling script
- **README.md** - Project documentation with setup instructions, configuration guide, and usage examples
- **.gitignore** - Git ignore patterns for Python, screenshots, environment files, etc.
- **.dockerignore** - Docker ignore patterns to optimize image size

## Implementation Plan

### Phase 1: Foundation
Set up the project structure with Docker configuration, dependency management, and environment variable handling. Create the base configuration system that loads GitHub credentials, target profile URL, and repository details. Establish the directory structure for source code, tests, and documentation. Initialize the Python project with uv for modern dependency management.

### Phase 2: Core Implementation
Implement the three core modules: screenshot capture using Playwright (with headless browser configuration), GitHub repository uploader (handling file commits via PyGithub), and bio updater (using GitHub REST API). Each module should be independently testable with clear interfaces. Add proper error handling, logging, and retry logic for network operations.

### Phase 3: Integration
Connect all modules in the main orchestration script that executes the complete workflow. Add scheduling capabilities (both cron and GitHub Actions options). Implement Docker containerization with proper health checks and volume mounting for persistent data. Create comprehensive tests that validate the entire pipeline end-to-end.

## Step by Step Tasks

### 1. Project Initialization and Structure
- Create project root directory structure (src/, tests/, specs/)
- Initialize Python project with uv
- Create .gitignore with Python, Docker, and environment file patterns
- Create .dockerignore for optimized Docker builds
- Set up basic README.md with project overview

### 2. Dependency Configuration
- Create pyproject.toml with project metadata
- Add dependencies: playwright, pygithub, python-dotenv, schedule, pillow
- Add dev dependencies: pytest, pytest-asyncio, pytest-mock, black, ruff
- Create requirements.txt for Docker compatibility
- Document all dependencies in README.md

### 3. Environment Configuration Setup
- Create .env.example with all required variables (GITHUB_TOKEN, GITHUB_USERNAME, GITHUB_REPO, PROFILE_URL, etc.)
- Implement src/config.py to load and validate environment variables
- Add configuration validation with clear error messages
- Write unit tests for config.py

### 4. Screenshot Capture Module
- Implement src/screenshot_capture.py with Playwright browser initialization
- Add function to navigate to GitHub profile URL
- Implement screenshot capture with configurable viewport size and quality
- Add wait logic for dynamic content loading
- Implement error handling for network failures and timeouts
- Write unit tests with mocked Playwright browser

### 5. GitHub Repository Uploader Module
- Implement src/github_uploader.py using PyGithub library
- Add function to authenticate with GitHub API using token
- Implement screenshot upload to specified repository path with timestamp naming
- Add logic to generate raw URL for uploaded file
- Implement retry logic for API failures
- Write unit tests with mocked GitHub API

### 6. Bio Updater Module
- Implement src/bio_updater.py for GitHub profile bio updates
- Add function to fetch current bio content
- Implement bio update logic that prepends/replaces screenshot link
- Add markdown formatting for the screenshot link
- Implement rollback capability if update fails
- Write unit tests with mocked GitHub API

### 7. Utility Functions
- Create src/utils.py with timestamp generation function
- Add file path utilities for screenshot naming
- Implement logging configuration with different levels (DEBUG, INFO, ERROR)
- Add helper functions for directory creation and cleanup
- Write unit tests for utility functions

### 8. Main Orchestration Script
- Implement src/main.py as the entry point
- Add workflow orchestration: capture → upload → update bio
- Implement error handling with notifications
- Add dry-run mode for testing without API calls
- Implement logging throughout the workflow
- Add command-line argument parsing for manual execution

### 9. Docker Configuration
- Create Dockerfile with Python 3.11+ base image
- Install system dependencies for Playwright (browsers)
- Copy project files and install Python dependencies
- Run playwright install for browser binaries
- Set up non-root user for security
- Configure container entry point

### 10. Docker Compose Setup
- Create docker-compose.yml for easy container management
- Configure environment variable passing
- Set up volume mounts for persistent logs
- Add health check configuration
- Configure restart policy for daily execution

### 11. Scheduling Implementation
- Create cron-schedule.sh script for cron-based scheduling
- Implement .github/workflows/daily-screenshot.yml for GitHub Actions
- Add documentation for both scheduling methods
- Configure timezone handling for consistent daily execution

### 12. Integration Tests
- Create tests/test_integration.py for end-to-end workflow
- Implement test with mocked external services
- Add tests for error scenarios and retry logic
- Test Docker container build and execution
- Validate screenshot quality and upload success

### 13. Documentation
- Complete README.md with detailed setup instructions
- Add configuration guide with all environment variables explained
- Include deployment options (local Docker, GitHub Actions, cloud hosting)
- Add troubleshooting section for common issues
- Include example screenshots and expected output

### 14. Validation and Testing
- Run all unit tests with pytest
- Execute integration tests
- Build Docker image and verify successful build
- Run container in test mode (dry-run)
- Perform full workflow test with actual GitHub API (test repository)
- Validate screenshot quality and bio update
- Execute validation commands to ensure zero regressions

## Testing Strategy

### Unit Tests
- **test_config.py**: Validate environment variable loading, missing variable detection, and default values
- **test_screenshot_capture.py**: Test browser initialization, navigation, screenshot capture, and error handling with mocked Playwright
- **test_github_uploader.py**: Test file upload, raw URL generation, and API error handling with mocked PyGithub
- **test_bio_updater.py**: Test bio fetching, updating, markdown formatting, and rollback with mocked GitHub API
- **test_utils.py**: Test timestamp generation, file naming, logging configuration, and helper functions

### Integration Tests
- **test_integration.py**: Test complete workflow from screenshot capture to bio update
- Test with mocked external services to avoid rate limits
- Validate data flow between modules
- Test error propagation and recovery
- Validate Docker container execution with test configuration
- Test scheduling logic (without waiting for actual schedule)

### Edge Cases
- Network timeout during screenshot capture
- GitHub API rate limiting
- Invalid GitHub token or insufficient permissions
- Repository not found or access denied
- Bio exceeds maximum length after adding screenshot link
- Concurrent execution prevention (locking mechanism)
- Browser crash or Playwright errors
- Malformed profile URL
- Screenshot upload failure with partial commits
- Empty or missing bio content

## Acceptance Criteria
- Docker container builds successfully without errors
- Application runs daily on schedule (configurable)
- Playwright successfully captures screenshot of specified GitHub profile with minimum 1920x1080 resolution
- Screenshot is uploaded to designated GitHub repository with timestamp-based filename (format: screenshot-YYYY-MM-DD-HH-MM-SS.png)
- Raw URL is correctly generated for uploaded screenshot
- GitHub bio is updated with markdown link to latest screenshot
- Previous screenshot links in bio are handled appropriately (replaced or maintained)
- All environment variables are properly documented and validated
- Error handling gracefully manages network failures and API errors
- Logging provides clear visibility into execution status
- Unit tests achieve >80% code coverage
- Integration tests validate end-to-end workflow
- README.md provides complete setup and deployment instructions
- Project runs successfully in Docker container without manual intervention

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Install dependencies
uv sync

# Run all unit tests with coverage
uv run pytest tests/ -v --cov=src --cov-report=term-missing

# Run linting checks
uv run ruff check src/ tests/
uv run black --check src/ tests/

# Build Docker image
docker build -t github-screenshot-automation .

# Run Docker container in dry-run mode (without API calls)
docker run --env-file .env -e DRY_RUN=true github-screenshot-automation

# Test screenshot capture module independently
uv run python -m src.screenshot_capture --profile-url https://github.com/fUmar3542 --output test_screenshot.png

# Validate Docker Compose configuration
docker-compose config

# Run full integration test
uv run pytest tests/test_integration.py -v -s

# Build and run container with docker-compose
docker-compose up --build

# Verify Playwright installation
docker run github-screenshot-automation playwright --version

# Test with actual GitHub API (using test repository)
docker run --env-file .env github-screenshot-automation

# Check logs for errors
docker logs github-screenshot-automation-container

# Validate screenshot file generation
ls -lh screenshots/

# Clean up test artifacts
docker-compose down
rm -rf screenshots/ test_screenshot.png
```

## Notes

### Dependencies to Install
- **playwright**: Browser automation for screenshot capture
- **pygithub**: GitHub API wrapper for uploads and bio updates
- **python-dotenv**: Environment variable management
- **schedule**: Task scheduling (for non-Docker cron alternative)
- **pillow**: Image processing and optimization
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **pytest-mock**: Mocking for tests
- **black**: Code formatting
- **ruff**: Fast Python linter

Install command: `uv add playwright pygithub python-dotenv schedule pillow`
Dev install: `uv add --dev pytest pytest-asyncio pytest-mock black ruff`

### Future Considerations
- Add support for multiple profiles with configuration file
- Implement screenshot comparison to detect visual changes
- Add notification system (email, Slack, Discord) for daily updates
- Create web dashboard to view screenshot history
- Add support for different screenshot regions (profile picture, contribution graph, etc.)
- Implement A/B testing with different bio formats
- Add analytics tracking for bio link clicks
- Support for custom screenshot overlays or watermarks
- Integrate with other social media platforms for cross-posting
- Add backup mechanism for screenshots to cloud storage (S3, CloudFlare R2)

### Security Considerations
- GitHub token should have minimal required permissions (public_repo, user)
- Use GitHub secrets for sensitive credentials in Actions workflow
- Implement token rotation reminders
- Avoid logging sensitive information
- Use read-only volume mounts where possible in Docker

### Performance Optimizations
- Use Playwright's screenshot caching to detect unchanged pages
- Implement incremental uploads (skip if screenshot identical to previous)
- Optimize Docker image size with multi-stage builds
- Use Alpine Linux base image for smaller footprint
- Compress screenshots before upload to reduce bandwidth

### Deployment Options
1. **Local Docker**: Run on personal machine with cron scheduling
2. **GitHub Actions**: Free daily execution with scheduled workflows
3. **Cloud Hosting**: Deploy to AWS ECS, Google Cloud Run, or Azure Container Instances
4. **VPS/Dedicated Server**: Deploy to DigitalOcean, Linode, or similar with Docker
5. **Kubernetes**: For advanced orchestration and scaling

### Error Recovery
- Implement exponential backoff for API retries
- Add alerting for consecutive failures
- Maintain audit log of all operations
- Create manual trigger mechanism for missed executions
