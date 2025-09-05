from __future__ import annotations
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from contextlib import contextmanager
from typing import Iterator, Optional

@contextmanager
def launch_browser(head: bool = True, slowmo: int = 0) -> Iterator[tuple[Browser, BrowserContext, Page]]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not head, slow_mo=slowmo)
        context = browser.new_context()
        page = context.new_page()
        try:
            yield browser, context, page
        finally:
            context.close()
            browser.close()
