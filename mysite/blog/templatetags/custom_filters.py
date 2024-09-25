import math
from django import template

register = template.Library()

@register.filter
def roundup(value):
    """Rounds up the value to the nearest integer."""
    return math.ceil(value)
