"""
@author: Gianfranco Micoli <micoli.gianfranco@gmail.com>
"""

from django import template
from django.http import HttpResponse
from Core import services

register = template.Library()

@register.filter
def render_accordion(value, arg):
    return HttpResponse(str({value, arg}))

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_item_attr(dictionary, key):
    return getattr(dictionary, key)

@register.filter
def lookup_field(lst, val):
	for item in lst:
		if item["field"] == val:
			return item
	return []

@register.filter
def sum_elements(dictionary, key):
	count = 0
	for mote in dictionary:
		count += int(dictionary[mote][key])
	return count
