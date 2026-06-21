"""
ترجمه دسته‌ای نام محصولات با OpenAI
"""
import json
import logging
import re
import time

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert in Iranian pharmacy, cosmetics, and supplement product catalogs.
Translate Persian product names into standard English product titles used on pharmacy e-commerce sites.

Rules:
1. Use correct Latin brand spellings (examples: Eurovital, Barij Essence, Serita, Erike, Signal, Meswak, Hydroderm, Prim, Biol, Golden Life, Vitalayer, Candid, Closeup, Gillette, Rexona, Jordan, 2080).
2. Include dosage/form: Capsules, Tablets, Syrup, Drops, Sachets, Cream, Gel, Shampoo, Serum, Sunscreen SPF, Toothpaste, Mouthwash, etc.
3. Include strength/count when present: 15mg, 250mg, 30 Tablets, 100ml.
4. Translate skin/hair types: oily skin, dry skin, sensitive, anti-aging, anti-hair loss.
5. Remove non-product words: new price, various types, promotional text.
6. Vitamin combos: A+D3+K2, B12, D3, Omega-3, Multivitamin.
7. Return ONLY a JSON array, no markdown:
   [{"fa":"persian name exactly as given","en":"English Product Name"}]
"""


def _get_api_config():
    api_key = getattr(settings, 'OPENAI_API_KEY', '') or getattr(settings, 'LLM_API_KEY', '')
    base_url = getattr(settings, 'OPENAI_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
    model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
    return api_key, base_url, model


def is_configured() -> bool:
    api_key, _, _ = _get_api_config()
    return bool(api_key)


def translate_batch(names: list[str], retries: int = 3) -> dict[str, str]:
    """
    ترجمه یک دسته نام فارسی → dict[fa, en]
    """
    api_key, base_url, model = _get_api_config()
    if not api_key:
        raise RuntimeError(
            'OPENAI_API_KEY در .env تنظیم نشده. '
            'مثال: OPENAI_API_KEY=sk-...'
        )

    user_content = (
        'Translate these Iranian pharmacy product names to standard English product titles:\n'
        + json.dumps(names, ensure_ascii=False)
    )

    for attempt in range(retries):
        try:
            response = requests.post(
                f'{base_url}/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': model,
                    'temperature': 0.1,
                    'messages': [
                        {'role': 'system', 'content': SYSTEM_PROMPT},
                        {'role': 'user', 'content': user_content},
                    ],
                },
                timeout=120,
            )
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content'].strip()
            content = re.sub(r'^```json\s*|\s*```$', '', content, flags=re.MULTILINE).strip()
            items = json.loads(content)
            result = {}
            for item in items:
                fa = item.get('fa', '').strip()
                en = item.get('en', '').strip()
                if fa and en:
                    result[fa] = en
            return result
        except Exception as exc:
            logger.warning('Translation batch attempt %s failed: %s', attempt + 1, exc)
            time.sleep(2 * (attempt + 1))

    return {}
