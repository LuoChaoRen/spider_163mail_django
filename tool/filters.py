from django import template
register = template.Library()

@register.filter(name='filter_if_in')  # name为使用filter时候的名字
def include_filter(value,values):
    return True if value in values else False
register.filter('include', include_filter)