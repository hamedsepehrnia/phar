from django.shortcuts import render
from django.views.decorators.cache import cache_page


@cache_page(60 * 60 * 24)  # Cache for 24 hours
def robots_txt(request):
    """Serve robots.txt with dynamic sitemap URL"""
    return render(request, 'robots.txt', content_type='text/plain')
