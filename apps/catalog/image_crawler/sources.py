"""Product image search sources — each uses isolated browser page."""
import logging
import re
import time
from difflib import SequenceMatcher
from urllib.parse import quote, quote_plus

from apps.catalog.image_crawler.browser import IsolatedBrowser

logger = logging.getLogger(__name__)

PRODUCT_IMAGE_PATTERN = re.compile(r'/images/[a-z0-9]{2,5}/[a-z0-9]+/', re.I)

TRUSTED_HOSTS = (
    'cloudinary.images-iherb.com', 'cloudinary.iherbpreprod.com',
    'image.torob.com',
    'dkstatics-public.digikala.com', 'digikala-products',
    'darukade.com', 'statics.darukade.com',
)


def normalize_text(text: str) -> str:
    return re.sub(r'[^a-z0-9\u0600-\u06ff ]', ' ', (text or '').lower())


def match_score(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def is_product_image_url(url: str) -> bool:
    if not url or not url.startswith('http'):
        return False
    lower = url.lower()
    if any(x in lower for x in ('logo', 'icon', 'banner', 'sprite', 'avatar', '.svg', 'adservice')):
        return False
    if 'cloudinary' in lower:
        if '/cms/' in lower or '/brand/' in lower:
            return False
        return bool(PRODUCT_IMAGE_PATTERN.search(url))
    return any(h in lower for h in TRUSTED_HOSTS)


def high_res_iherb(url: str) -> str:
    url = url.replace('cloudinary.iherbpreprod.com', 'cloudinary.images-iherb.com')
    return re.sub(r'/upload/[^/]+/', '/upload/w_800,f_auto,q_auto:good/', url, count=1)


def torob_search_query(name_fa: str) -> str:
    """نام ساده‌شده برای جستجوی ترب."""
    q = re.sub(r'[+_]', ' ', name_fa)
    q = re.sub(r'قیمت\s*جدید|انواع', '', q, flags=re.I)
    return re.sub(r'\s+', ' ', q).strip()[:100]


class TorobSource:
    """ترب — بهترین منبع برای محصولات داروخانه ایران."""
    MIN_SCORE = 0.28
    SEARCH_URL = 'https://torob.com/search/?query={query}'

    def search(self, browser: IsolatedBrowser, name_fa: str, name_en: str = '') -> dict | None:
        query = quote(torob_search_query(name_fa))

        def _run(page):
            browser.goto_stable(
                page,
                self.SEARCH_URL.format(query=query),
                wait_selector='img[src*="image.torob.com"]',
            )
            time.sleep(2)
            page.evaluate('window.scrollTo(0, 600)')
            time.sleep(1)
            items = browser.safe_evaluate(page, '''() => {
                return [...document.querySelectorAll('img[src*="image.torob.com"]')]
                    .map(img => ({
                        src: img.src,
                        alt: (img.alt || img.getAttribute('title') || '').trim()
                    }))
                    .filter(x => x.alt && x.src)
                    .slice(0, 20);
            }''')
            best = None
            best_score = 0.0
            for item in items:
                score = max(
                    match_score(item.get('alt', ''), name_fa),
                    match_score(item.get('alt', ''), name_en),
                )
                if score > best_score:
                    best_score = score
                    best = item
            if best and best_score >= self.MIN_SCORE:
                src = best['src'].replace('/0x176.jpg', '/0x512.jpg')
                return {
                    'image_url': src,
                    'product_url': self.SEARCH_URL.format(query=query),
                    'match_score': best_score,
                    'source': 'torob',
                }
            return None

        try:
            return browser.run(_run, locale='fa-IR')
        except Exception as exc:
            logger.warning('Torob failed for %r: %s', name_fa[:40], exc)
            return None


class DigikalaSource:
    MIN_SCORE = 0.32

    def search(self, browser: IsolatedBrowser, name_fa: str, name_en: str = '') -> dict | None:
        query = quote(name_fa)

        def _run(page):
            browser.goto_stable(
                page,
                f'https://www.digikala.com/search/{query}/',
                wait_selector='a[href*="/product/"]',
            )
            time.sleep(2)
            cards = browser.safe_evaluate(page, '''() => {
                return [...document.querySelectorAll('a[href*="/product/dkp"]')]
                    .slice(0, 12)
                    .map(a => ({
                        href: a.href,
                        title: (a.getAttribute('aria-label') || a.innerText || '').trim().slice(0, 120)
                    }))
                    .filter(x => x.title);
            }''')
            best = None
            best_score = 0.0
            for card in cards:
                score = max(
                    match_score(card.get('title', ''), name_fa),
                    match_score(card.get('title', ''), name_en),
                )
                if score > best_score:
                    best_score = score
                    best = card
            if not best or best_score < self.MIN_SCORE:
                return None
            browser.goto_stable(page, best['href'], wait_selector='meta[property="og:image"]')
            time.sleep(1)
            og = page.locator('meta[property="og:image"]').get_attribute('content')
            if og and 'digikala-products' in og:
                return {
                    'image_url': og.split('?')[0] + '?x-oss-process=image/quality,q_90',
                    'product_url': best['href'],
                    'match_score': best_score,
                    'source': 'digikala',
                }
            return None

        try:
            return browser.run(_run, locale='fa-IR')
        except Exception as exc:
            logger.warning('Digikala failed for %r: %s', name_fa[:40], exc)
            return None


class IHerbSource:
    MIN_SCORE = 0.22
    SEARCH_URL = 'https://de.iherb.com/search?kw={query}'

    def search(self, browser: IsolatedBrowser, query: str, name_en: str) -> dict | None:
        def _run(page):
            browser.goto_stable(
                page,
                self.SEARCH_URL.format(query=quote_plus(query)),
                wait_selector='a[href*="/pr/"]',
            )
            time.sleep(2)
            page.evaluate('window.scrollTo(0, 1200)')
            time.sleep(2)
            links = browser.safe_evaluate(page, '''() =>
                [...new Set([...document.querySelectorAll('a[href*="/pr/"]')].map(a => a.href))].slice(0, 4)
            ''')
            for link in links:
                try:
                    browser.goto_stable(page, link)
                    time.sleep(1)
                    title = page.title()
                    og_list = browser.safe_evaluate(page, '''() =>
                        [...document.querySelectorAll('meta[property="og:image"]')].map(m => m.content)
                    ''')
                    og = og_list[0] if og_list else ''
                except Exception:
                    continue
                og = og.replace('cloudinary.iherbpreprod.com', 'cloudinary.images-iherb.com')
                if not is_product_image_url(og):
                    continue
                score = match_score(title, name_en)
                if score >= self.MIN_SCORE or match_score(query, name_en) > 0.45:
                    return {
                        'image_url': high_res_iherb(og),
                        'product_url': link,
                        'match_score': max(score, 0.25),
                        'source': 'iherb',
                    }
            return None

        try:
            return browser.run(_run, locale='en-US')
        except Exception as exc:
            logger.warning('iHerb failed for %r: %s', query[:40], exc)
            return None


class DdgSource:
    """فقط fallback — با throttle سنگین."""
    MIN_SCORE = 0.28
    _blocked = False

    def search(self, query: str, name_en: str) -> dict | None:
        if self._blocked:
            return None
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.images(query, max_results=6, size='Large'))
            best = None
            best_score = 0.0
            for item in results:
                url = item.get('image', '')
                if not is_product_image_url(url):
                    continue
                score = match_score(item.get('title', ''), name_en)
                if score > best_score:
                    best_score = score
                    best = item
            if best and best_score >= self.MIN_SCORE:
                return {
                    'image_url': best['image'],
                    'product_url': best.get('url', ''),
                    'match_score': best_score,
                    'source': 'ddg',
                }
        except Exception as exc:
            msg = str(exc).lower()
            if '403' in msg or 'ratelimit' in msg:
                DdgSource._blocked = True
                logger.warning('DDG rate-limited — disabled for this session.')
            else:
                logger.warning('DDG failed: %s', exc)
        return None
