# myproject/jinja2.py

from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse

from .templatetags import my_tags  # We'll define this next

def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
    })
    
    # Register custom filters
    # myproject/jinja2.py

    env.filters.update({
        # ... other filters ...
        'big_number': my_tags.format_big_number,
    })

    return env
