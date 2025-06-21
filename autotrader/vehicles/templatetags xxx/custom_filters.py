from django import template

register = template.Library()

@register.filter
def labelize(value):
    """Replaces underscores with spaces and title-cases the result."""
    return str(value).replace('_', ' ').title()