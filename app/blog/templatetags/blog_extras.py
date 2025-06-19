from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """
    Returns the string split by arg.
    Usage: {{ value|split:"," }}
    """
    return value.split(arg) 