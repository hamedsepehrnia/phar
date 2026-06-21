"""
Context processor to provide site settings to all templates
"""
from .models import SiteSettings
from .site_defaults import SiteSettingsProxy


def site_settings(request):
    """Return SiteSettings instance as `site_settings` in templates."""
    try:
        settings = SiteSettings.get_settings()
    except Exception:
        settings = None
    return {'site_settings': SiteSettingsProxy(settings)}
