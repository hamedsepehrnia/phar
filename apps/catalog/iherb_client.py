"""Backward-compatible re-exports."""
from apps.catalog.product_image_fetcher import (  # noqa: F401
    DEFAULT_CACHE_DIR,
    DEFAULT_MANIFEST_PATH,
    IHerbImageFetcher,
    ProductImageFetcher,
    attach_image_to_product,
)
from apps.catalog.product_translations import product_name_key  # noqa: F401
