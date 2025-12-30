"""
اسکریپت تست برای بررسی اسلاگ‌های فارسی
"""
from urllib.parse import quote, unquote

# تست URL encoding/decoding
persian_slugs = [
    "داروی-ضد-درد",
    "ویتامین-ب12", 
    "آنتی-بیوتیک-قوی",
    "مولتی-ویتامین-کودکان"
]

print("=== تست URL Encoding ===")
for slug in persian_slugs:
    encoded = quote(slug, safe='')
    decoded = unquote(encoded)
    
    print(f"اصلی: {slug}")
    print(f"Encoded: {encoded}")
    print(f"Decoded: {decoded}")
    print(f"برابری: {slug == decoded}")
    print("---")

print("\n=== تست Regex Patterns ===")
import re

# الگوی قدیمی
old_pattern = r'^product/(?P<slug>[-\w\u0600-\u06FF]+)/$'

# الگوی جدید
new_pattern = r'^product/(?P<slug>[^/]+)/$'

test_urls = [
    "product/داروی-ضد-درد/",
    f"product/{quote('داروی-ضد-درد', safe='')}/",
    "product/painkiller-medicine/",
]

for url in test_urls:
    old_match = re.match(old_pattern, url)
    new_match = re.match(new_pattern, url)
    
    print(f"URL: {url}")
    print(f"الگوی قدیمی: {'✅' if old_match else '❌'}")
    print(f"الگوی جدید: {'✅' if new_match else '❌'}")
    if new_match:
        print(f"Slug: {new_match.group('slug')}")
    print("---")