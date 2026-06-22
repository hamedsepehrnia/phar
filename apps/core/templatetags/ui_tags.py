"""
Template tags for shared UI components.
"""
from django import template
from django.urls import NoReverseMatch, reverse

register = template.Library()


def _resolve_url(url_ref):
    url_ref = url_ref.strip()
    if url_ref.startswith('/') or url_ref.startswith('http'):
        return url_ref
    try:
        return reverse(url_ref)
    except NoReverseMatch:
        return url_ref


@register.inclusion_tag('partials/breadcrumb.html', takes_context=True)
def site_breadcrumb(context, *segments):
    """
    Usage:
      {% site_breadcrumb "خانه|core:home" "فروشگاه|catalog:shop" "تماس با ما" %}

    Last segment without "|" is the current page.
    """
    items = context.get('breadcrumb_items')
    if items:
        return {'items': items}

    parsed = []
    for segment in segments:
        if '|' in segment:
            label, url_ref = segment.split('|', 1)
            parsed.append({'label': label.strip(), 'url': _resolve_url(url_ref)})
        else:
            parsed.append({'label': segment.strip(), 'url': None})
    return {'items': parsed}
