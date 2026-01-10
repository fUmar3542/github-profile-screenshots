"""Unit tests for screenshot capture module."""

from unittest.mock import AsyncMock, patch

import pytest

from src.screenshot_capture import ScreenshotCapture, capture_screenshot


class TestScreenshotCapture:
    """Test cases for ScreenshotCapture class."""

    def test_init_default_params(self):
        """Test initialization with default parameters."""
        capturer = ScreenshotCapture()
        assert capturer.viewport_width == 1920
        assert capturer.viewport_height == 1080
        assert capturer.quality == 90

    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        capturer = ScreenshotCapture(viewport_width=2560, viewport_height=1440, quality=95)
        assert capturer.viewport_width == 2560
        assert capturer.viewport_height == 1440
        assert capturer.quality == 95

    @pytest.mark.asyncio
    @patch("src.screenshot_capture.async_playwright")
    async def test_capture_success(self, mock_playwright, tmp_path):
        """Test successful screenshot capture."""
        # Setup mocks
        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_browser = AsyncMock()

        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.screenshot = AsyncMock()

        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        # Create capturer
        capturer = ScreenshotCapture()
        output_path = tmp_path / "test_screenshot.png"

        # Capture
        result = await capturer.capture("https://github.com/testuser", output_path)

        # Assertions
        assert result == output_path
        mock_page.goto.assert_called_once()
        mock_page.wait_for_selector.assert_called_once()
        mock_page.screenshot.assert_called_once()
        mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.screenshot_capture.async_playwright")
    async def test_capture_navigation_failure(self, mock_playwright, tmp_path):
        """Test screenshot capture with navigation failure."""
        # Setup mocks
        mock_page = AsyncMock()
        mock_page.goto.side_effect = Exception("Navigation failed")

        mock_context = AsyncMock()
        mock_context.new_page.return_value = mock_page

        mock_browser = AsyncMock()
        mock_browser.new_context.return_value = mock_context

        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        # Create capturer
        capturer = ScreenshotCapture()
        output_path = tmp_path / "test_screenshot.png"

        # Should raise exception
        with pytest.raises(Exception) as excinfo:
            await capturer.capture("https://github.com/testuser", output_path)

        assert "Navigation failed" in str(excinfo.value)

    @patch("src.screenshot_capture.asyncio.run")
    def test_capture_sync(self, mock_asyncio_run, tmp_path):
        """Test synchronous capture wrapper."""
        output_path = tmp_path / "test_screenshot.png"
        mock_asyncio_run.return_value = output_path

        capturer = ScreenshotCapture()
        result = capturer.capture_sync("https://github.com/testuser", output_path)

        assert result == output_path
        mock_asyncio_run.assert_called_once()

    @patch("src.screenshot_capture.ScreenshotCapture.capture_sync")
    def test_capture_screenshot_function(self, mock_capture_sync, tmp_path):
        """Test convenience function for screenshot capture."""
        output_path = tmp_path / "test_screenshot.png"
        mock_capture_sync.return_value = output_path

        result = capture_screenshot("https://github.com/testuser", output_path)

        assert result == output_path
        mock_capture_sync.assert_called_once()
