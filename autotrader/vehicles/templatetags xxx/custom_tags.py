from django import template
register = template.Library()

@register.filter
def get_list(dict_data, key):
    return dict_data.getlist(key)
