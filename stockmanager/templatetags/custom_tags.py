from django import template

register = template.Library()

@register.filter
def get_user_holding(holdings, user):
    return holdings.filter(user=user).first()
