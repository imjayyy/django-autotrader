from django import template

register = template.Library()

@register.filter
def add_thousand(value, amount=2000):
    try:
        return value + int(amount)
    except:
        return value

@register.filter
def format_big_number(value):
    try:
        number = float(value)
        if number.is_integer():
            return "{:,.0f}".format(number)
        else:
            return "{:,.2f}".format(number)
    except (TypeError, ValueError):
        return value
