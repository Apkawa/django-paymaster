# coding: utf-8
from __future__ import unicode_literals



try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


