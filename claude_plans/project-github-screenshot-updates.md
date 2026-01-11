# Feature: Streamlined GitHub Profile Screenshot Automation

## Feature Description
This feature streamlines the GitHub profile screenshot automation by removing unnecessary bio update functionality, capturing full page screenshots starting from the Popular repositories section, and consolidating storage to a single repository. The updated system will scroll to the Popular repositories section before capturing the full page, store screenshots in the profile README repository, and update only the README file with relative screenshot links.

## User Story
As a GitHub profile maintainer
I want to automatically capture and display my profile starting from the popular repositories section
So that visitors to my profile can see my key projects and activity without managing multiple repositories or updating my bio

## Problem Statement
The current implementation has three main issues:
1. **Unnecessary Bio Updates**: The system updates the GitHub bio with screenshot URLs, which is not needed since the screenshot is already displayed in the profile README
2. **Wrong Starting Point**: Screenshots capture from the top of the profile page when we want to start from the "Popular repositories" section that highlights key projects
3. **Multi-Repository Complexity**: Using a separate repository for screenshot storage adds unnecessary complexity and results in absolute URLs in the README instead of cleaner relative paths

## Solution Statement
Simplify and enhance the automation by:
1. **Removing Bio Logic**: Eliminate all bio update functionality, focusing solely on README updates in the fUmar3542/fUmar3542 repository
2. **Optimized Screenshot Capture**: Scroll to the "Popular repositories" section, then capture the full page from that point downward
3. **Single Repository Storage**: Store screenshots in fUmar3542/fUmar3542/screenshots/ and use relative paths (./screenshots/2026-01-10.png) in the README, eliminating the need for a separate repository

## Relevant Files
The following files need modifications to implement this feature:

- **src/main.py** (lines 1-187)
  - Remove bio_updater import and instantiation
  - Remove Step 3 (bio update) from workflow
  - Update orchestration to work with profile README repository only
  - Remove bio-related error handling and rollback logic

- **src/bio_updater.py** (lines 1-269)
  - Rename to `readme_updater.py` for clarity
  - Remove bio-specific references and rename class from BioUpdater to ReadmeUpdater
  - Update to work exclusively with fUmar3542/fUmar3542 repository
  - Modify screenshot link format to use relative paths (./screenshots/filename.png)
  - Remove prepend parameter logic (no longer needed)

- **src/screenshot_capture.py** (lines 1-175)
  - Add scrolling logic to navigate to "Popular repositories" section
  - After scrolling, take full page screenshot from that position

- **src/config.py** (lines 1-137)
  - Remove GITHUB_REPO configuration (no longer needed)
  - Update to use hardcoded profile repository (fUmar3542/fUmar3542)
  - Update documentation to reflect changes

- **src/github_uploader.py** (lines 1-183)
  - Update to upload screenshots to fUmar3542/fUmar3542/screenshots/ directory
  - Modify to return relative path instead of raw URL
  - Simplify URL generation since it's always the same repository

- **.env.example** (lines 1-24)
  - Remove GITHUB_REPO configuration
  - Update comments to reflect new simplified structure
  - Update documentation for SCREENSHOT_PATH

- **README.md** (lines 1-338)
  - Update feature descriptions to reflect README-only updates
  - Remove bio update references
  - Update configuration documentation
  - Update "How It Works" section to describe new workflow
  - Update troubleshooting section

- **Dockerfile** (lines 1-89)
  - No changes required (already optimized)

- **.github/workflows/daily-screenshot.yml** (lines 1-76)
  - Remove GITHUB_REPO secret usage
  - Update environment configuration
  - Update job description

### New Files
- **src/readme_updater.py**
  - Renamed and refactored version of bio_updater.py
  - Focused on profile README updates only

## Implementation Plan

### Phase 1: Foundation
Remove bio update functionality and establish README-only update pattern. This includes renaming the bio_updater module to readme_updater, removing all bio-specific logic, and updating the configuration to work with a single repository.

### Phase 2: Core Implementation
Update screenshot capture to scroll to the Popular repositories section before taking a full page screenshot. Implement scrolling logic, waiting for content to settle, then capturing the entire visible page from that scroll position.

### Phase 3: Integration
Update storage to use the profile README repository (fUmar3542/fUmar3542) with relative paths. Modify the uploader to work with the profile repository, update the main orchestration flow, and ensure all components work together seamlessly.

## Step by Step Tasks

### Step 1: Rename and Refactor Bio Updater to README Updater
- Rename `src/bio_updater.py` to `src/readme_updater.py`
- Rename `BioUpdater` class to `ReadmeUpdater`
- Remove `update_bio` method and rename to `update_readme`
- Remove `prepend` parameter (no longer needed)
- Update screenshot link format to use relative paths: `./screenshots/{filename}`
- Update repository to be hardcoded to `fUmar3542/fUmar3542`
- Remove rollback functionality (simpler updates don't need it)
- Update all docstrings and comments to reflect README focus
- Update logger name from `bio` to `readme`

### Step 2: Update Main Orchestration
- Update `src/main.py` to import `ReadmeUpdater` instead of `BioUpdater`
- Remove Step 3 (bio update) section
- Consolidate upload and README update into unified flow
- Remove bio-related error handling and rollback logic
- Update to pass screenshot filename to README updater
- Simplify workflow to: capture → upload → update README → cleanup

### Step 3: Update Screenshot Capture to Scroll Then Capture Full Page
- Update `src/screenshot_capture.py` capture method:
  - After initial page load, add scroll logic to reach "Popular repositories" section
  - Use `page.locator('h2:has-text("Popular repositories")')` or similar selector to find the section header
  - Scroll the section into view with `scroll_into_view_if_needed()`
  - Add 2-3 second delay with `page.wait_for_timeout(2000)` for dynamic content to settle
  - Take FULL PAGE screenshot from this scroll position using `page.screenshot(full_page=True)`
  - Do NOT use bounding box clipping or clip parameter
  - The screenshot will capture everything visible from the Popular repositories section downward
- Viewport size can remain standard (1920x1080)
- Add error handling for cases where popular repositories section isn't found
- Log clear messages about scrolling to the section before capture

### Step 4: Update Configuration Module
- Remove `github_repo` field from `Config` dataclass in `src/config.py`
- Add `profile_repo` field with default value `"fUmar3542/fUmar3542"`
- Remove `GITHUB_REPO` from required environment variables
- Update `from_env` method to remove GITHUB_REPO parsing
- Remove repository format validation
- Update docstrings to reflect single-repository approach

### Step 5: Update GitHub Uploader for Profile Repository
- Update `src/github_uploader.py` to use profile repository `fUmar3542/fUmar3542`
- Modify `upload_screenshot` to upload to `screenshots/` directory within the profile repo
- Change return value to relative path format: `./screenshots/{filename}`
- Remove `_generate_raw_url` method (no longer needed)
- Ensure screenshots directory exists in the fUmar3542/fUmar3542 repository
- Update docstrings and comments

### Step 6: Update Environment Configuration
- Update `.env.example` to remove `GITHUB_REPO` variable
- Add comment explaining screenshots are stored in profile repository (fUmar3542/fUmar3542/screenshots/)
- Update `SCREENSHOT_PATH` documentation to clarify it's a directory name within the profile repo
- Update all environment variable descriptions

### Step 7: Update Tests for README Updater
- Rename `tests/test_bio_updater.py` to `tests/test_readme_updater.py`
- Update all test imports and class references
- Update test cases to verify relative path format (./screenshots/...)
- Remove bio-specific test cases
- Add tests for relative path generation
- Update test fixtures and mocks to use fUmar3542/fUmar3542 repository
- Ensure all tests pass with new implementation

### Step 8: Update Tests for Screenshot Capture
- Update `tests/test_screenshot_capture.py` for scroll-then-capture functionality
- Add test case for scrolling to Popular repositories section
- Add test case for waiting after scroll (2-3 second delay)
- Add test case for full page screenshot after scrolling (verify full_page=True is used)
- Add test case for handling missing Popular repositories section
- Mock Playwright page interactions for scroll and wait
- Verify NO bounding box or clipping logic is used

### Step 9: Update Tests for GitHub Uploader
- Update `tests/test_github_uploader.py` for profile repository usage
- Update tests to verify upload to fUmar3542/fUmar3542/screenshots/
- Update tests to verify relative path returns (./screenshots/...)
- Remove raw URL generation tests
- Update mocks to reflect new repository structure
- Add tests for screenshots directory creation in profile repo

### Step 10: Update Integration Tests
- Update `tests/test_integration.py` to reflect new workflow
- Remove bio update integration tests
- Add tests for README update with relative paths in fUmar3542/fUmar3542
- Update test fixtures for profile repository
- Verify end-to-end flow without bio updates
- Test screenshot capture with scroll to Popular repositories then full page capture
- Verify screenshot is stored in fUmar3542/fUmar3542/screenshots/

### Step 11: Update Documentation
- Update `README.md` to remove all bio update references
- Update "Features" section to describe README-only updates
- Update "How It Works" section with new 3-step workflow (capture with scroll → upload to profile repo → update README)
- Update "Configuration Reference" to remove GITHUB_REPO
- Add documentation about screenshots being stored in fUmar3542/fUmar3542/screenshots/
- Update "Troubleshooting" to remove bio-related issues
- Add note about relative paths and single repository approach
- Update examples and quick start guide

### Step 12: Update GitHub Actions Workflow
- Update `.github/workflows/daily-screenshot.yml`
- Remove `GITHUB_REPO` from secrets usage
- Update environment file creation to exclude GITHUB_REPO
- Update job description to reflect README-only updates in fUmar3542/fUmar3542
- Ensure workflow still runs with simplified configuration

### Step 13: Update Docker Configuration
- Review `Dockerfile` for any bio-related references (none expected)
- Verify Docker build still works with updated code
- Test Docker container with new configuration
- Update docker-compose.yml if needed (verify no GITHUB_REPO references)

### Step 14: Run All Validation Commands
- Execute all validation commands listed below
- Fix any issues that arise
- Verify zero regressions
- Ensure all tests pass
- Validate end-to-end functionality

## Testing Strategy

### Unit Tests
- **test_readme_updater.py**: Verify ReadmeUpdater correctly formats relative paths, updates profile README in fUmar3542/fUmar3542, handles repository creation
- **test_screenshot_capture.py**: Verify scrolling to Popular repositories section, waiting for content to settle, capturing full page (not clipped section)
- **test_github_uploader.py**: Verify upload to fUmar3542/fUmar3542/screenshots/, relative path generation (./screenshots/...)
- **test_config.py**: Verify config loads without GITHUB_REPO, profile_repo defaults to fUmar3542/fUmar3542
- **test_utils.py**: Verify utility functions remain functional

### Integration Tests
- **test_integration.py**: Verify complete workflow (scroll → capture full page → upload to profile repo → update README → cleanup) without bio updates
- Test with real GitHub API (using test repository if available)
- Verify relative paths work in README markdown
- Verify screenshot captures full page starting from Popular repositories section
- Test error handling and recovery

### Edge Cases
- Profile with no popular repositories section (should handle gracefully)
- Network timeouts during screenshot capture
- GitHub API rate limiting
- Profile README doesn't exist in fUmar3542/fUmar3542 (create new)
- Profile repository fUmar3542/fUmar3542 doesn't exist (create new)
- Invalid relative paths in markdown
- Screenshot file size limits
- Popular repositories section not visible or takes time to load
- Dynamic content loading delays after scrolling

## Acceptance Criteria
1. ✅ Bio updater code is completely removed from the codebase
2. ✅ README updater only updates fUmar3542/fUmar3542/README.md
3. ✅ Screenshots capture full page starting from the Popular repositories section (scroll to section, then full_page=True)
4. ✅ Screenshots are stored in fUmar3542/fUmar3542/screenshots/ directory
5. ✅ README uses relative paths (./screenshots/filename.png) instead of absolute URLs
6. ✅ GITHUB_REPO configuration is removed from all files
7. ✅ All tests pass with zero failures
8. ✅ Docker container builds and runs successfully
9. ✅ GitHub Actions workflow runs without errors
10. ✅ Documentation accurately reflects the new implementation
11. ✅ No references to bio updates remain in code or documentation
12. ✅ GITHUB_TOKEN authentication works for all operations
13. ✅ Daily scheduling capability is maintained
14. ✅ Code coverage remains above 80%
15. ✅ Screenshot storage is in profile repository (fUmar3542/fUmar3542), not separate repository

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.
```bash
# Run all tests with coverage
uv run pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

# Verify no bio_updater references remain
grep -r "bio_updater" --include="*.py" --include="*.md" . || echo "✅ No bio_updater references found"

# Verify no BioUpdater class references remain
grep -r "BioUpdater" --include="*.py" . || echo "✅ No BioUpdater class references found"

# Verify ReadmeUpdater exists
grep -r "ReadmeUpdater" src/ --include="*.py" | head -n 5

# Verify relative path format in readme_updater
grep -r "./screenshots/" src/readme_updater.py || echo "❌ Relative path format not found"

# Verify profile repository is hardcoded to fUmar3542/fUmar3542
grep -r "fUmar3542/fUmar3542" src/ --include="*.py" | head -n 3

# Verify GITHUB_REPO removed from config
grep "GITHUB_REPO" src/config.py && echo "❌ GITHUB_REPO still in config" || echo "✅ GITHUB_REPO removed from config"

# Verify GITHUB_REPO removed from .env.example
grep "GITHUB_REPO" .env.example && echo "❌ GITHUB_REPO still in .env.example" || echo "✅ GITHUB_REPO removed from .env.example"

# Run specific test files
uv run pytest tests/test_readme_updater.py -v
uv run pytest tests/test_screenshot_capture.py -v
uv run pytest tests/test_github_uploader.py -v
uv run pytest tests/test_integration.py -v

# Test Docker build
docker build -t github-screenshot-test . --no-cache

# Verify Docker build success
docker images | grep github-screenshot-test

# Lint code (if ruff is available)
uv run ruff check src/ tests/ || echo "Ruff not available, skipping lint"

# Format code check (if black is available)
uv run black --check src/ tests/ || echo "Black not available, skipping format check"

# Verify main.py imports ReadmeUpdater
grep "from .readme_updater import ReadmeUpdater" src/main.py || echo "❌ ReadmeUpdater import not found"

# Verify popular repositories scroll logic exists
grep -A 5 "Popular repositories" src/screenshot_capture.py || echo "❌ Popular repositories logic not found"

# Verify full_page screenshot (not clipped)
grep "full_page=True" src/screenshot_capture.py || echo "❌ full_page=True not found"

# Verify NO bounding box or clip logic
grep -i "bounding_box\|clip=" src/screenshot_capture.py && echo "❌ Should not use bounding box or clip" || echo "✅ No bounding box/clip logic"

# Count test files
find tests/ -name "test_*.py" -type f | wc -l

# Verify no broken imports
uv run python -c "from src.main import main; from src.readme_updater import ReadmeUpdater; from src.screenshot_capture import ScreenshotCapture; print('✅ All imports successful')"

# Check for TODO or FIXME comments added during implementation
grep -r "TODO\|FIXME" src/ tests/ --include="*.py" || echo "✅ No TODO/FIXME comments"

# Verify GitHub Actions workflow syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/daily-screenshot.yml'))" && echo "✅ Workflow YAML is valid"

# Test dry-run mode
uv run python -m src.main --dry-run --log-level DEBUG
```

## Notes

### Migration Considerations
- The existing github-profile-screenshots repository can remain for historical purposes but won't receive new screenshots
- All new screenshots will be stored in fUmar3542/fUmar3542/screenshots/
- Existing workflows using the old repository structure should be updated
- Any external references to raw.githubusercontent.com URLs will need updating to relative paths

### Performance Optimizations
- Scrolling to Popular repositories adds 2-3 seconds to screenshot capture
- Full page screenshots may be larger than section-only captures
- Standard viewport (1920x1080) is sufficient
- Consider image compression if file sizes become too large

### Future Enhancements
- Add configuration to switch between different starting scroll positions (top, popular repos, contribution graph)
- Support for multiple profile layouts (organization vs personal)
- Automatic cropping to remove unnecessary whitespace
- Screenshot comparison to avoid unnecessary README updates when content hasn't changed
- Option to capture only specific sections vs full page

### Dependencies
- No new Python packages required
- Existing Playwright, PyGithub, and python-dotenv are sufficient
- Docker image size should remain approximately the same

### Security
- GITHUB_TOKEN still requires `public_repo` scope for repository operations
- No additional security concerns introduced
- Single repository approach reduces attack surface

### Repository Structure After Implementation
```
fUmar3542/fUmar3542/
├── README.md (contains ![Profile](./screenshots/2026-01-10.png))
└── screenshots/
    ├── 2026-01-10.png (full page screenshot starting from Popular repositories)
    ├── 2026-01-09.png
    └── ...
```

### Relative Path Benefits
1. **Simpler**: No need for raw.githubusercontent.com URLs
2. **Portable**: Works in any GitHub view (file browser, README rendering)
3. **Cleaner**: Easier to read in markdown source
4. **Single Source of Truth**: Everything in one repository (fUmar3542/fUmar3542)

### Screenshot Capture Implementation Details
- The screenshot will capture the full page starting from the "Popular repositories" section
- Implementation approach:
  1. Navigate to profile URL
  2. Wait for page to load completely
  3. Locate the "Popular repositories" section using CSS selectors
  4. Scroll the section into view using `scroll_into_view_if_needed()`
  5. Wait 2-3 seconds for dynamic content to settle
  6. Take full page screenshot with `page.screenshot(full_page=True)`
- This approach ensures the screenshot starts from the Popular repositories and includes everything below it

### Testing Notes
- Use test repository (fUmar3542/test-profile or similar) for development
- Mock Playwright page interactions to avoid actual browser launches in CI
- Integration tests should be optional (require INTEGRATION_TEST=true env var)
- Add VCR.py or similar for recording/replaying GitHub API interactions in tests
- Test with profiles that have varying numbers of popular repositories (0, 3, 6, etc.)