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
        if number:
            return "{:,.0f}".format(number)
        else:
            return "{:,.2f}".format(number)
    except (TypeError, ValueError):
        return value


@register.filter
def get_discounted_price(price, discount):
    if not price or not discount:
        return format_big_number(price)
    price = float(price) - float(discount)

    return format_big_number(price) 

