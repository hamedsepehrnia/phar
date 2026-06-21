"""Playwright browser with isolated context/page per operation."""
import logging
import time

logger = logging.getLogger(__name__)


class IsolatedBrowser:
    """هر عملیات جستجو = context + page جدید (بدون state مشترک)."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser = None

    def __enter__(self):
        from playwright.sync_api import sync_playwright
        self._playwright = sync_playwright().start()
        try:
            self._browser = self._playwright.chromium.launch(
                channel='chrome',
                headless=self.headless,
            )
        except Exception:
            self._browser = self._playwright.firefox.launch(headless=self.headless)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def run(self, fn, *, locale: str = 'en-US', user_agent: str | None = None):
        if not self._browser:
            raise RuntimeError('Browser not started')
        ua = user_agent or (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        context = self._browser.new_context(
            locale=locale,
            user_agent=ua,
            extra_http_headers={'Accept-Language': f'{locale},en;q=0.9'},
        )
        page = context.new_page()
        page.set_default_timeout(45000)
        try:
            return fn(page)
        finally:
            context.close()

    def goto_stable(self, page, url: str, wait_selector: str | None = None):
        page.goto(url, wait_until='domcontentloaded')
        if wait_selector:
            try:
                page.wait_for_selector(wait_selector, timeout=20000)
            except Exception:
                pass
        try:
            page.wait_for_load_state('networkidle', timeout=12000)
        except Exception:
            time.sleep(2)

    def safe_evaluate(self, page, expression: str, retries: int = 2):
        last_exc = None
        for attempt in range(retries):
            try:
                return page.evaluate(expression)
            except Exception as exc:
                last_exc = exc
                if 'destroyed' in str(exc).lower() and attempt < retries - 1:
                    time.sleep(1.5)
                    continue
                raise exc
        raise last_exc
