from django import template

register = template.Library()

@register.filter
def add_thousand(value, amount=2000):
    try:
        return value + int(amount)
    except:
        return value
