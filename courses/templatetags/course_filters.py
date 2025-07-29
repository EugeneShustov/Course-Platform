from django import template

register = template.Library()

@register.filter
def completed_for_user(modules, user):
    return [m for m in modules.all() if user in m.completed.all()]
