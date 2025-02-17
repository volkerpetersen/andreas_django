from django import template

register = template.Library()

@register.filter(name='replace')
def replace(value, arg):
    old, new = arg.split(',')
    return value.replace(old, new)

@register.filter(name='multi_replace')
def multi_replace(value, arg):
    replacements = arg.split(',')
    for old, new in zip(replacements[::2], replacements[1::2]):
        value = value.replace(old, new)
    return value