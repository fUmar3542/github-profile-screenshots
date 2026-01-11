"""Screenshot capture module using Playwright for browser automation."""

import asyncio
import logging
from pathlib import Path

from playwright.async_api import Browser, async_playwright

from .utils import ensure_directory_exists

logger = logging.getLogger("github_screenshot_automation.screenshot")


class ScreenshotCapture:
    """Handles GitHub profile screenshot capture using Playwright."""

    def __init__(
        self,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        quality: int = 90,
    ):
        """
        Initialize screenshot capture configuration.

        Args:
            viewport_width: Browser viewport width in pixels
            viewport_height: Browser viewport height in pixels
            quality: Screenshot quality (1-100)
        """
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.quality = quality
        self.browser: Browser | None = None

    async def capture(self, profile_url: str, output_path: Path) -> Path:
        """
        Capture screenshot of GitHub profile.

        Args:
            profile_url: GitHub profile URL to screenshot
            output_path: Path where screenshot will be saved

        Returns:
            Path to saved screenshot

        Raises:
            Exception: If screenshot capture fails
        """
        logger.info(f"Starting screenshot capture for {profile_url}")

        try:
            async with async_playwright() as playwright:
                # Launch browser in headless mode
                logger.debug("Launching browser")
                browser = await playwright.chromium.launch(headless=True)

                # Create browser context
                context = await browser.new_context(
                    viewport={
                        "width": self.viewport_width,
                        "height": self.viewport_height,
                    },
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                )

                # Create new page
                page = await context.new_page()

                # Navigate to profile
                logger.info(f"Navigating to {profile_url}")
                await page.goto(profile_url, wait_until="networkidle", timeout=30000)

                # Wait for profile content to load
                logger.debug("Waiting for profile content")
                await page.wait_for_selector(".js-profile-editable-replace", timeout=10000)

                # Additional wait for dynamic content
                await asyncio.sleep(2)

                # Hide README section to capture from Popular repositories onwards
                logger.info("Hiding README section before screenshot")

                try:
                    # Use JavaScript to hide README section with multiple selectors
                    logger.debug("Executing JavaScript to hide README sections")
                    await page.evaluate("""
                        // Hide the README preview section (article tag)
                        const readmePreview = document.querySelector('article.markdown-body');
                        if (readmePreview) {
                            readmePreview.style.display = 'none';
                            console.log('Hidden: article.markdown-body');
                        }

                        // Hide the entire readme container with data attribute
                        const readmeContainer = document.querySelector('div[data-test-selector="profile-readme-container"]');
                        if (readmeContainer) {
                            readmeContainer.style.display = 'none';
                            console.log('Hidden: profile-readme-container');
                        }

                        // Hide the JS profile readme container
                        const readmeSection = document.querySelector('.js-profile-readme-container');
                        if (readmeSection) {
                            readmeSection.style.display = 'none';
                            console.log('Hidden: js-profile-readme-container');
                        }

                        // Hide any h2 that says "README.md" and its parent container
                        const readmeHeaders = document.querySelectorAll('h2');
                        readmeHeaders.forEach(header => {
                            if (header.textContent.includes('README')) {
                                const container = header.closest('div[class*="readme"]') || header.closest('div.border');
                                if (container) {
                                    container.style.display = 'none';
                                    console.log('Hidden: README header container');
                                }
                            }
                        });
                    """)
                    logger.info("README sections hidden via JavaScript")

                    # Wait for layout to adjust after hiding
                    await page.wait_for_timeout(2000)

                    # Find and scroll to the Popular repositories section
                    logger.info("Scrolling to Popular repositories section")
                    popular_repos = page.locator('h2:has-text("Popular repositories")')
                    if await popular_repos.count() > 0:
                        await popular_repos.scroll_into_view_if_needed()
                        logger.info("Scrolled to Popular repositories section")
                    else:
                        # Try alternate selectors
                        popular_repos = page.locator('h2.f4.mb-2.text-normal')
                        if await popular_repos.count() > 0:
                            await popular_repos.first.scroll_into_view_if_needed()
                            logger.info("Scrolled to repositories section")
                        else:
                            logger.warning("Could not find Popular repositories heading")

                    # Wait for content to settle after scrolling
                    await page.wait_for_timeout(1000)

                except Exception as e:
                    logger.warning(f"Error during README hiding: {e}")
                    logger.warning("Will capture full page with README visible")

                # Ensure output directory exists
                ensure_directory_exists(output_path.parent)

                # Capture full page screenshot (will start from visible content after hiding)
                logger.info(f"Capturing full page screenshot to {output_path}")
                await page.screenshot(
                    path=str(output_path),
                    full_page=True,
                    type="png",
                )

                logger.info(f"Screenshot saved successfully to {output_path}")

                # Restore hidden sections using JavaScript
                try:
                    logger.debug("Restoring README sections visibility")
                    await page.evaluate("""
                        // Restore the README preview section (article tag)
                        const readmePreview = document.querySelector('article.markdown-body');
                        if (readmePreview) {
                            readmePreview.style.display = 'block';
                            console.log('Restored: article.markdown-body');
                        }

                        // Restore the entire readme container with data attribute
                        const readmeContainer = document.querySelector('div[data-test-selector="profile-readme-container"]');
                        if (readmeContainer) {
                            readmeContainer.style.display = 'block';
                            console.log('Restored: profile-readme-container');
                        }

                        // Restore the JS profile readme container
                        const readmeSection = document.querySelector('.js-profile-readme-container');
                        if (readmeSection) {
                            readmeSection.style.display = 'block';
                            console.log('Restored: js-profile-readme-container');
                        }

                        // Restore any h2 README containers
                        const readmeHeaders = document.querySelectorAll('h2');
                        readmeHeaders.forEach(header => {
                            if (header.textContent.includes('README')) {
                                const container = header.closest('div[class*="readme"]') || header.closest('div.border');
                                if (container) {
                                    container.style.display = 'block';
                                    console.log('Restored: README header container');
                                }
                            }
                        });
                    """)
                    logger.info("Hidden sections restored")
                except Exception as e:
                    logger.warning(f"Error restoring hidden sections: {e}")
                    # Not critical since browser will be closed anyway

                # Close browser
                await browser.close()

                return output_path

        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            raise

    def capture_sync(self, profile_url: str, output_path: Path) -> Path:
        """
        Synchronous wrapper for capture method.

        Args:
            profile_url: GitHub profile URL to screenshot
            output_path: Path where screenshot will be saved

        Returns:
            Path to saved screenshot
        """
        return asyncio.run(self.capture(profile_url, output_path))


def capture_screenshot(
    profile_url: str,
    output_path: Path,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
    quality: int = 90,
) -> Path:
    """
    Convenience function to capture a screenshot.

    Args:
        profile_url: GitHub profile URL to screenshot
        output_path: Path where screenshot will be saved
        viewport_width: Browser viewport width in pixels
        viewport_height: Browser viewport height in pixels
        quality: Screenshot quality (1-100)

    Returns:
        Path to saved screenshot
    """
    capturer = ScreenshotCapture(viewport_width, viewport_height, quality)
    return capturer.capture_sync(profile_url, output_path)


if __name__ == "__main__":
    import argparse
    import sys

    from .utils import setup_logging

    parser = argparse.ArgumentParser(description="Capture GitHub profile screenshot")
    parser.add_argument("--profile-url", required=True, help="GitHub profile URL")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--width", type=int, default=1920, help="Viewport width")
    parser.add_argument("--height", type=int, default=1080, help="Viewport height")
    parser.add_argument("--quality", type=int, default=90, help="Screenshot quality")
    parser.add_argument("--log-level", default="INFO", help="Logging level")

    args = parser.parse_args()

    setup_logging(args.log_level)

    try:
        output = capture_screenshot(
            args.profile_url,
            Path(args.output),
            args.width,
            args.height,
            args.quality,
        )
        print(f"Screenshot saved to: {output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
