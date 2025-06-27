# stockmanager/templatetags/custom_tags.py

from django import template

register = template.Library()

@register.filter
def get_user_holding(userholdings, user):
    return userholdings.filter(user=user).first()
