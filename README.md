# GitHub Profile Screenshot Automation

Automated system to capture daily screenshots of GitHub profiles, upload them to a repository, and update the profile bio with the latest screenshot link.

## Features

- **Automated Screenshot Capture**: Uses Playwright to capture public GitHub profile screenshots
- **GitHub Integration**: Automatically uploads screenshots to a designated repository
- **Profile README Updates**: Updates your GitHub profile README with the latest screenshot link
- **Docker Support**: Fully containerized for consistent execution across environments
- **Multiple Scheduling Options**: GitHub Actions, cron, or manual execution
- **Comprehensive Testing**: Unit and integration tests with >80% coverage
- **Error Handling**: Retry logic and rollback capabilities for robustness

## Prerequisites

- Python 3.11 or higher
- GitHub personal access token with `public_repo` and `user` permissions
- Docker (optional, for containerized deployment)
- uv package manager (recommended)

## Quick Start

### 1. Installation

Clone the repository and install dependencies:

```bash
# Clone the repository
git clone <repository-url>
cd GitHub

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install Playwright browsers
uv run playwright install chromium
```

### 2. Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# GitHub Authentication
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username

# GitHub Repository for Screenshot Storage
GITHUB_REPO=username/repository-name
SCREENSHOT_PATH=screenshots

# Target Profile to Screenshot
PROFILE_URL=https://github.com/username

# Screenshot Configuration (optional)
VIEWPORT_WIDTH=1920
VIEWPORT_HEIGHT=1080
SCREENSHOT_QUALITY=90

# Application Settings (optional)
DRY_RUN=false
LOG_LEVEL=INFO
```

### 3. Run

Execute the automation:

```bash
# Run with default configuration
uv run python -m src.main

# Run in dry-run mode (no API calls, skip upload/bio update)
uv run python -m src.main --dry-run

# Run with custom log level for debugging
uv run python -m src.main --log-level DEBUG
```

**That's it!** The system uses your `GITHUB_TOKEN` from the `.env` file for both API operations (upload, bio update) and browser authentication. No manual login or additional setup required.

## Docker Deployment

### Build and Run

```bash
# Build Docker image
docker build -t github-screenshot-automation .

# Run with docker-compose
docker-compose up --build

# Run single execution
docker run --env-file .env github-screenshot-automation
```

### Docker Compose

The `docker-compose.yml` file provides easy container management:

```bash
# Start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

## Scheduling Options

### Option 1: GitHub Actions (Recommended)

GitHub Actions provides free daily execution with no infrastructure required.

1. Add the following secrets to your GitHub repository:
   - `GH_TOKEN`: Your GitHub personal access token
   - `GH_USERNAME`: Your GitHub username
   - `GH_REPO`: Repository for screenshots (format: `owner/repo`)
   - `PROFILE_URL`: GitHub profile URL to screenshot

2. The workflow in `.github/workflows/daily-screenshot.yml` runs automatically at midnight UTC.

3. Manual trigger:
   - Go to Actions tab in your repository
   - Select "Daily GitHub Profile Screenshot"
   - Click "Run workflow"

### Option 2: Cron (Linux/macOS)

Add the provided script to your crontab:

```bash
# Make the script executable
chmod +x cron-schedule.sh

# Edit crontab
crontab -e

# Add this line to run daily at midnight
0 0 * * * /path/to/GitHub/cron-schedule.sh
```

### Option 3: Docker Compose Scheduler

Use the built-in scheduler service:

```bash
docker-compose --profile scheduler up -d
```

## Configuration Reference

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub personal access token | `ghp_xxxxxxxxxxxx` |
| `GITHUB_USERNAME` | Your GitHub username | `johndoe` |
| `GITHUB_REPO` | Repository for screenshots | `johndoe/screenshots` |
| `PROFILE_URL` | Profile URL to screenshot | `https://github.com/johndoe` |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SCREENSHOT_PATH` | `screenshots` | Path in repository for screenshots |
| `VIEWPORT_WIDTH` | `1920` | Browser viewport width (800-3840) |
| `VIEWPORT_HEIGHT` | `1080` | Browser viewport height (600-2160) |
| `SCREENSHOT_QUALITY` | `90` | Screenshot quality (1-100) |
| `DRY_RUN` | `false` | Skip API calls for testing |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `SCHEDULE_TIME` | `00:00` | Daily execution time (24-hour format) |
| `TIMEZONE` | `UTC` | Timezone for scheduling |

## Development

### Running Tests

```bash
# Run all tests with coverage
uv run pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_config.py -v

# Run integration tests only
uv run pytest tests/test_integration.py -v
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type checking (if mypy is installed)
uv run mypy src/
```

## Project Structure

```
GitHub/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main orchestration script
│   ├── config.py            # Configuration management
│   ├── screenshot_capture.py # Playwright screenshot module
│   ├── github_uploader.py   # GitHub upload module
│   ├── bio_updater.py       # Bio update module
│   └── utils.py             # Utility functions
├── tests/
│   ├── test_config.py
│   ├── test_utils.py
│   ├── test_screenshot_capture.py
│   ├── test_github_uploader.py
│   ├── test_bio_updater.py
│   └── test_integration.py
├── .github/
│   └── workflows/
│       └── daily-screenshot.yml
├── screenshots/             # Local screenshot storage
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

## How It Works

1. **Screenshot Capture**: Playwright launches a headless Chrome browser, navigates to the specified GitHub profile URL, and captures a full-page screenshot of the public profile view.

2. **Upload**: The screenshot is uploaded to the designated GitHub repository with a timestamped filename (e.g., `screenshot-2024-01-15-10-30-45.png`) using your GitHub personal access token.

3. **README Update**: The GitHub API updates your profile README, prepending a markdown image link to the latest screenshot. Previous screenshot links are automatically removed.

4. **Cleanup**: Old local screenshots are cleaned up, keeping only the 30 most recent ones.

This approach is fully automated and works perfectly in Docker/CI environments without any manual intervention.

## Troubleshooting

### Common Issues

**Error: Missing required environment variables**
- Ensure all required variables are set in your `.env` file
- Check for typos in variable names

**Error: GitHub API rate limiting**
- The application includes retry logic with exponential backoff
- Consider reducing execution frequency

**Error: Bio exceeds maximum length**
- GitHub bios have a 160-character limit
- The application automatically truncates content while preserving the screenshot link

**Error: Playwright browser not found**
- Run `uv run playwright install chromium` to install browser binaries
- In Docker, browsers are installed automatically during image build

**Screenshot capture fails**
- Check internet connectivity
- Verify the profile URL is correct and accessible
- Ensure your `GITHUB_TOKEN` is valid and has the required permissions
- Increase timeout values if network is slow
- Check the logs with `--log-level DEBUG` for detailed error information

### Debug Mode

Run with debug logging to see detailed execution information:

```bash
uv run python -m src.main --log-level DEBUG
```

## Security Considerations

- **Token Permissions**: Use a token with minimal required permissions (`public_repo`, `user`)
- **Token Storage**: Never commit `.env` files or tokens to version control
- **GitHub Secrets**: Use GitHub Secrets for Actions workflows to securely store your `GITHUB_TOKEN`
- **Container Security**: The Docker image runs as a non-root user for enhanced security
- **Token Security**: The GitHub token is only used during script execution and is not persisted to disk

## Performance Optimization

- **Screenshot Caching**: Consider implementing comparison logic to skip uploads for unchanged screenshots
- **Image Compression**: Adjust `SCREENSHOT_QUALITY` to balance file size and visual quality
- **Docker Image Size**: The multi-stage build keeps the image size optimized
- **Cleanup**: Automatic cleanup prevents local storage bloat

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass and code is formatted
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [Playwright](https://playwright.dev/) for reliable browser automation
- Uses [PyGithub](https://github.com/PyGithub/PyGithub) for GitHub API integration
- Containerized with [Docker](https://www.docker.com/) for consistent deployment

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section above

---

**Made with ❤️ for GitHub users who love automation**
