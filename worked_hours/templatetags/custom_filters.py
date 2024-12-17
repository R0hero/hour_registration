from django import template
import datetime

register = template.Library()

@register.filter
def format_duration(value):
    if isinstance(value, datetime.timedelta):
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if minutes == 0:
            return f"{hours} hours"
        return f"{hours} hours, {minutes} minutes"
    return value

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def total_duration(daily_hours, date):
    if date in daily_hours:
        total = sum(daily_hours[date].values(), datetime.timedelta())
        return total
    return datetime.timedelta()

@register.filter
def is_day(date, day_name):
    return date.strftime('%A') == day_name

@register.filter
def timedelta_difference(value, arg):
    if isinstance(value, datetime.timedelta) and isinstance(arg, datetime.timedelta):
        return value - arg
    return None

@register.filter
def absolute_timedelta(value):
    return datetime.timedelta(seconds=abs(value.total_seconds()))