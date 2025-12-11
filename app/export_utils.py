"""Export utilities for converting character sheets to PDF and images

This module provides functions to export character sheets to various formats
using Playwright for HTML rendering.
"""

import asyncio
import os
from pathlib import Path
from typing import Literal, Optional
from playwright.async_api import async_playwright, Browser, Page
import logging

logger = logging.getLogger(__name__)

# Browser instance cache (reuse for performance)
_browser_instance: Optional[Browser] = None


async def get_browser() -> Browser:
    """Get or create a shared browser instance for better performance"""
    global _browser_instance

    if _browser_instance is None or not _browser_instance.is_connected():
        playwright = await async_playwright().start()
        _browser_instance = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']  # Required for Railway/containers
        )

    return _browser_instance


async def export_character_sheet(
    url: str,
    format: Literal['pdf', 'png'],
    character_name: str,
    wait_for_selector: str = ".character-sheet",
    viewport_width: int = 1920,
    viewport_height: int = 1080
) -> bytes:
    """
    Export a character sheet to PDF or PNG format

    Args:
        url: The full URL of the character sheet to export
        format: Output format ('pdf' or 'png')
        character_name: Name of the character (for filename)
        wait_for_selector: CSS selector to wait for before capturing
        viewport_width: Browser viewport width
        viewport_height: Browser viewport height

    Returns:
        bytes: The exported file content

    Raises:
        Exception: If export fails
    """
    browser = await get_browser()
    context = await browser.new_context(
        viewport={'width': viewport_width, 'height': viewport_height},
        device_scale_factor=2  # Higher quality output
    )

    try:
        page = await context.new_page()

        # Navigate to the character sheet
        logger.info(f"Navigating to {url} for export")
        await page.goto(url, wait_until='networkidle', timeout=30000)

        # Wait for the character sheet to load
        await page.wait_for_selector(wait_for_selector, timeout=10000)

        # Give Alpine.js time to fully hydrate and render
        await asyncio.sleep(1)

        # Hide elements that shouldn't appear in exports
        await page.evaluate("""
            // Hide save indicators, edit buttons, and other UI chrome
            const elementsToHide = document.querySelectorAll(`
                .save-indicator,
                .btn-delete,
                .upload-btn,
                .image-upload-overlay,
                .portrait-upload-controls,
                .export-buttons-fixed,
                button[type="submit"]:not(.export-btn),
                .storyteller-banner
            `);
            elementsToHide.forEach(el => el.style.display = 'none');

            // Ensure all images are loaded
            const images = document.querySelectorAll('img');
            await Promise.all(Array.from(images).map(img => {
                if (img.complete) return Promise.resolve();
                return new Promise(resolve => {
                    img.addEventListener('load', resolve);
                    img.addEventListener('error', resolve);
                });
            }));
        """)

        # Additional wait for any lazy-loaded content
        await asyncio.sleep(0.5)

        if format == 'pdf':
            # Export as PDF
            pdf_bytes = await page.pdf(
                format='A4',
                print_background=True,
                margin={
                    'top': '0.5cm',
                    'right': '0.5cm',
                    'bottom': '0.5cm',
                    'left': '0.5cm'
                },
                prefer_css_page_size=False
            )
            return pdf_bytes

        elif format == 'png':
            # Export as PNG (full page screenshot)
            screenshot_bytes = await page.screenshot(
                full_page=True,
                type='png'
            )
            return screenshot_bytes

        else:
            raise ValueError(f"Unsupported format: {format}")

    except Exception as e:
        logger.error(f"Error exporting character sheet: {e}")
        raise
    finally:
        await context.close()


async def export_character_sheet_element(
    url: str,
    format: Literal['pdf', 'png'],
    character_name: str,
    selector: str = ".character-sheet",
    viewport_width: int = 1920,
    viewport_height: int = 1080
) -> bytes:
    """
    Export a specific element of a character sheet

    This is useful for exporting just the sheet content without the page chrome.

    Args:
        url: The full URL of the character sheet to export
        format: Output format ('pdf' or 'png')
        character_name: Name of the character (for filename)
        selector: CSS selector of the element to capture
        viewport_width: Browser viewport width
        viewport_height: Browser viewport height

    Returns:
        bytes: The exported file content
    """
    browser = await get_browser()
    context = await browser.new_context(
        viewport={'width': viewport_width, 'height': viewport_height},
        device_scale_factor=2
    )

    try:
        page = await context.new_page()

        logger.info(f"Navigating to {url} for element export")
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await page.wait_for_selector(selector, timeout=10000)
        await asyncio.sleep(1)

        # Hide unwanted elements
        await page.evaluate("""
            const elementsToHide = document.querySelectorAll(`
                .save-indicator,
                .btn-delete,
                .upload-btn,
                .image-upload-overlay,
                button[type="submit"]:not(.export-btn)
            `);
            elementsToHide.forEach(el => el.style.display = 'none');
        """)

        element = await page.query_selector(selector)
        if not element:
            raise ValueError(f"Element not found: {selector}")

        if format == 'png':
            screenshot_bytes = await element.screenshot(type='png')
            return screenshot_bytes
        elif format == 'pdf':
            # For PDF, we still need to use page.pdf as elements can't be directly converted
            # But we can scroll to the element first
            await element.scroll_into_view_if_needed()
            pdf_bytes = await page.pdf(
                format='A4',
                print_background=True,
                margin={'top': '0.5cm', 'right': '0.5cm', 'bottom': '0.5cm', 'left': '0.5cm'}
            )
            return pdf_bytes
        else:
            raise ValueError(f"Unsupported format: {format}")

    except Exception as e:
        logger.error(f"Error exporting element: {e}")
        raise
    finally:
        await context.close()


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """
    Sanitize a character name for use in a filename

    Args:
        name: The character name
        max_length: Maximum filename length

    Returns:
        str: Sanitized filename-safe string
    """
    # Remove or replace invalid filename characters
    invalid_chars = '<>:"/\\|?*'
    sanitized = name
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')

    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')

    # Remove any non-ASCII characters
    sanitized = ''.join(char for char in sanitized if ord(char) < 128)

    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    # Default if empty
    if not sanitized:
        sanitized = "character"

    return sanitized
