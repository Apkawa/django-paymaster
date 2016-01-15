# coding: utf-8
from __future__ import unicode_literals

from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.template import Library
from django.utils.safestring import mark_safe

try:
    from django.utils import simplejson as json
except ImportError:
    import json

register = Library()


def json_filter(object):
    json_string = None
    if isinstance(object, QuerySet):
        json_string = serialize('json', object)
    else:
        json_string =json.dumps(object)
    return mark_safe(json_string)


register.filter('json', json_filter)
