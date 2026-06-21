"""
Crawler production-grade برای تصویر واقعی محصول.

زنجیره منابع (پیش‌فرض):
  1. Digikala (نام فارسی — دقیق‌ترین برای محصولات ایرانی)
  2. iHerb (نام انگلیسی AI — یک query)
  3. DDG (فقط با --enable-ddg)

بدون Google Images scraping. بدون fallback عکس چرت.
"""
import json
import logging
from io import BytesIO
from pathlib import Path
from typing import Any

import requests
from django.conf import settings
from PIL import Image

from apps.catalog.image_crawler.browser import IsolatedBrowser
from apps.catalog.image_crawler.rate_limit import CrawlRateLimiter
from apps.catalog.image_crawler.sources import DdgSource, DigikalaSource, IHerbSource, TorobSource, is_product_image_url
from apps.catalog.product_translations import (
    build_search_queries_from_english,
    get_english_name,
    product_name_key,
)

logger = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = Path(settings.BASE_DIR) / 'data' / 'seed' / 'product_images'
DEFAULT_MANIFEST_PATH = Path(settings.BASE_DIR) / 'data' / 'seed' / 'product_image_manifest.json'


class ProductImageFetcher:
    """
    هر محصول:
    - cache hit → skip
    - source chain با retry
    - manifest بعد از هر محصول ذخیره (resume-safe)
    """

    def __init__(
        self,
        cache_dir: Path | None = None,
        manifest_path: Path | None = None,
        headless: bool = True,
        enable_ddg: bool = False,
        limiter: CrawlRateLimiter | None = None,
    ):
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.manifest_path = manifest_path or DEFAULT_MANIFEST_PATH
        self.headless = headless
        self.enable_ddg = enable_ddg
        self.limiter = limiter or CrawlRateLimiter()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest = self._load_manifest()
        self._browser: IsolatedBrowser | None = None
        self._torob = TorobSource()
        self._digikala = DigikalaSource()
        self._iherb = IHerbSource()
        self._ddg = DdgSource()

    def _load_manifest(self) -> dict[str, Any]:
        if self.manifest_path.exists():
            with open(self.manifest_path, encoding='utf-8') as fh:
                return json.load(fh)
        return {'version': 3, 'products': {}}

    def save_manifest(self):
        with open(self.manifest_path, 'w', encoding='utf-8') as fh:
            json.dump(self.manifest, fh, ensure_ascii=False, indent=2)

    def __enter__(self):
        self._browser = IsolatedBrowser(headless=self.headless)
        self._browser.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            self._browser.__exit__(exc_type, exc_val, exc_tb)
            self._browser = None

    def resolve_image_path(self, entry: dict) -> Path | None:
        """Resolve image path — manifest may contain old absolute paths from dev."""
        image_file = entry.get('image_file')
        if image_file:
            path = Path(image_file)
            if path.exists():
                return path

        key = entry.get('key')
        if key:
            candidate = self.cache_dir / f'{key}.jpg'
            if candidate.exists():
                return candidate

        if image_file:
            candidate = self.cache_dir / Path(image_file).name
            if candidate.exists():
                return candidate

        return None

    def get_cached_entry(self, name_fa: str) -> dict | None:
        entry = self.manifest.get('products', {}).get(product_name_key(name_fa))
        if not entry:
            return None
        resolved = self.resolve_image_path(entry)
        if resolved:
            return {**entry, 'image_file': str(resolved)}
        return entry

    def fetch_product_image(
        self,
        name_fa: str,
        name_en: str | None = None,
        force: bool = False,
        item_index: int = 0,
    ) -> dict[str, Any]:
        key = product_name_key(name_fa)
        existing = self.manifest.get('products', {}).get(key)
        if existing and existing.get('status') == 'ok' and not force:
            if self.resolve_image_path(existing):
                return existing

        if not name_en:
            name_en = get_english_name(name_fa) or ''

        queries = build_search_queries_from_english(name_en) if name_en else []
        primary_query = queries[0] if queries else name_en

        result = {
            'name_fa': name_fa,
            'name_en': name_en,
            'key': key,
            'queries': queries,
            'status': 'not_found',
            'source': '',
            'image_url': '',
            'product_url': '',
            'image_file': '',
            'search_query': '',
            'match_score': 0,
            'attempts': [],
        }

        if not name_en:
            result['status'] = 'no_translation'
            self._persist(key, result)
            return result

        self.limiter.maybe_batch_pause(item_index)
        hit = self._run_source_chain(name_fa, name_en, primary_query, result)
        if hit:
            result.update(hit)
            result['search_query'] = hit.get('search_query', primary_query)

        if result.get('image_url'):
            saved = self._download_image(result['image_url'], key)
            if saved:
                result['image_file'] = str(saved)
                result['status'] = 'ok'
            else:
                result['status'] = 'download_failed'
        else:
            result['status'] = 'not_found'

        self._persist(key, result)
        self.limiter.throttle()
        return result

    def _run_source_chain(
        self,
        name_fa: str,
        name_en: str,
        primary_query: str,
        result: dict,
    ) -> dict | None:
        if not self._browser:
            raise RuntimeError('Fetcher must be used as context manager')

        chain = [
            ('torob', lambda: self._torob.search(self._browser, name_fa, name_en)),
            ('iherb', lambda: self._iherb.search(self._browser, primary_query, name_en)),
            ('digikala', lambda: self._digikala.search(self._browser, name_fa, name_en)),
        ]
        if self.enable_ddg:
            chain.append(
                ('ddg', lambda: self._ddg.search(primary_query, name_en)),
            )

        for source_name, fn in chain:
            for attempt in range(2):
                try:
                    hit = fn()
                    result['attempts'].append({
                        'source': source_name,
                        'attempt': attempt + 1,
                        'ok': bool(hit),
                    })
                    if hit:
                        hit['search_query'] = primary_query if source_name != 'digikala' else name_fa
                        return hit
                    break
                except Exception as exc:
                    result['attempts'].append({
                        'source': source_name,
                        'attempt': attempt + 1,
                        'error': str(exc)[:200],
                    })
                    logger.warning('%s attempt %s failed: %s', source_name, attempt + 1, exc)
                    self.limiter.throttle(multiplier=1.5 + attempt)
        return None

    def _persist(self, key: str, result: dict):
        self.manifest.setdefault('products', {})[key] = result
        self.save_manifest()

    def _download_image(self, url: str, key: str) -> Path | None:
        try:
            response = requests.get(
                url,
                timeout=30,
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; DavajooCrawler/1.0)',
                    'Accept': 'image/*,*/*',
                },
            )
            response.raise_for_status()
            raw = response.content
            img = Image.open(BytesIO(raw))
            img.verify()
            img = Image.open(BytesIO(raw))
            if img.width < 120 or img.height < 120:
                return None
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            out_path = self.cache_dir / f'{key}.jpg'
            img.save(out_path, 'JPEG', quality=90, optimize=True)
            return out_path
        except Exception as exc:
            logger.error('Download failed %s: %s', url[:80], exc)
            return None


IHerbImageFetcher = ProductImageFetcher


def attach_image_to_product(product, image_path: str | Path, alt_text: str = ''):
    from django.core.files import File
    from apps.catalog.models import ProductImage

    path = Path(image_path)
    if not path.exists():
        return None

    ProductImage.objects.filter(product=product).delete()
    pi = ProductImage(
        product=product,
        alt_text=alt_text or product.name,
        is_main=True,
        sort_order=0,
    )
    with open(path, 'rb') as fh:
        pi.image.save(f'{product.slug}.jpg', File(fh), save=True)
    return pi
