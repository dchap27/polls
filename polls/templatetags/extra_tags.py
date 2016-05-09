from django import template
from django.template.defaultfilters import stringfilter # to convert the filter to string
register = template.Library()

@register.simple_tag
def percent(value,value2):
    new_percent = (value * 100)/value2
    return int(new_percent)

@register.filter
@stringfilter
def capitalize(value):
    return value.capitalize()
