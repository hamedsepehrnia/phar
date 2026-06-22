# آرشیو تم رنگی سایت

دو تم در این پروژه ثبت شده‌اند. تم فعال در `static/css/cyan-theme-override.css` و `static/css/cyan-utilities.css` است.

## تم فعلی — Brand Teal (فعال از 2025-06-23)

| نقش | Hex |
|-----|-----|
| Primary | `#0BB2C4` |
| Hover | `#0999A8` |
| Dark | `#077D89` |
| Light | `#4FD3E0` |
| Background Dark | `#071419` |
| White Text | `#FFFFFF` |

**فایل مرجع:** `static/css/archives/theme-brand-teal-current.css`

**Footer (فعلی):**
```css
background: linear-gradient(135deg, #071419 0%, #077D89 55%, #0BB2C4 100%);
```

**theme-color (فعلی):** `#0BB2C4`

---

## تم قبلی — Sky/Cyan (قبل از 2025-06-23)

| نقش | Hex |
|-----|-----|
| Primary | `#0ea5e9` |
| Hover | `#0284c7` |
| Dark | `#0c4a6e` |
| Light 50 | `#f0f9ff` |
| Light 100 | `#e0f2fe` |
| Light 200 | `#bae6fd` |
| Light 300 | `#7dd3fc` |
| Light 400 | `#38bdf8` |
| Accent | `#06b6d4`, `#22d3ee`, `#0891b2` |
| Shadow | `rgba(14, 165, 233, …)` |
| Hover shadow | `rgba(2, 132, 199, …)` |

**فایل مرجع:** `static/css/archives/theme-sky-cyan-legacy.css`

**Footer (قدیمی):**
```css
background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 50%, #22d3ee 100%);
color: #e0f2fe;
```

**theme-color (قدیمی):** `#0ea5e9`

---

## بازگردانی به تم Sky/Cyan

### ۱. جایگزینی متغیرهای `:root`

محتوای بلوک `:root` در `static/css/cyan-theme-override.css` را با بلوک داخل `theme-sky-cyan-legacy.css` (بدون کلاس `.theme-sky-cyan-legacy`) عوض کنید.

### ۲. جایگزینی hex در CSS و قالب‌ها

از ریشه پروژه:

```bash
# CSS
for f in static/css/cyan-theme-override.css static/css/cyan-utilities.css; do
  sed -i \
    -e 's/#0BB2C4/#0ea5e9/gi' \
    -e 's/#0999A8/#0284c7/gi' \
    -e 's/#077D89/#0c4a6e/gi' \
    -e 's/#4FD3E0/#38bdf8/gi' \
    -e 's/#A8ECF2/#bae6fd/gi' \
    -e 's/#D4F4F7/#e0f2fe/gi' \
    -e 's/#EAF9FB/#f0f9ff/gi' \
    -e 's/#2BC9D8/#38bdf8/gi' \
    -e 's/rgba(11, 178, 196/rgba(14, 165, 233/g' \
    -e 's/rgba(9, 153, 168/rgba(2, 132, 199/g' \
    "$f"
done

# قالب‌ها (در صورت نیاز)
grep -rl '#0BB2C4\|#0999A8\|#077D89\|#071419' templates | while read f; do
  sed -i \
    -e 's/#0BB2C4/#0ea5e9/gi' \
    -e 's/#0999A8/#0284c7/gi' \
    -e 's/#077D89/#0c4a6e/gi' \
    -e 's/#071419/#0c4a6e/gi' \
    -e 's/#4FD3E0/#22d3ee/gi' \
    -e 's/#EAF9FB/#f0f9ff/gi' \
    -e 's/#D4F4F7/#e0f2fe/gi' \
    "$f"
done
```

### ۳. فوتر و SEO

- `templates/partials/footer.html` — گرادیان و glow بنفش قدیمی (در git history یا این سند)
- `templates/partials/seo_meta.html` — `theme-color` را `#0ea5e9` بگذارید

### ۴. کش

```bash
python manage.py collectstatic --noinput --settings=config.settings.prod
```

نسخه query string در `templates/base.html` برای CSS را یک عدد بالا ببرید.

---

## نکته

- فایل‌های `static/css/archives/` در production لود نمی‌شوند؛ فقط مرجع هستند.
- امن‌ترین بازگشت: `git checkout` روی commit قبل از تغییر تم (اگر commit شده باشد).
