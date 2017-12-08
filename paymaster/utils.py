# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import six
import base64
import binascii
import hashlib

from uuid import uuid4
from datetime import datetime

from django.utils.encoding import smart_text, smart_bytes
from simplecrypt import encrypt, decrypt, DecryptionException
from django.utils.module_loading import import_string

from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from . import settings
from . import logger


def calculate_hash(data, hashed_fields, password=None, hash_method=None):
    password = password or settings.PAYMASTER_PASSWORD
    hash_method = hash_method or settings.PAYMASTER_HASH_METHOD

    _line = u';'.join(map(str, [data.get(key) or '' for key in hashed_fields]))
    _line += u';{0}'.format(password)
    _hash = getattr(hashlib, hash_method)(_line.encode('utf-8'))
    _hash = base64.b64encode(smart_bytes(_hash.digest())).strip()
    return smart_text(_hash)


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def format_dt(dt):
    return dt.strftime(DATETIME_FORMAT)


def parse_datetime(dt_string):
    from dateutil.parser import parse
    return parse(dt_string)


def decode_payer(enc):
    """ Декодирование пользователя-инициатора платежа """
    try:
        _chr = binascii.unhexlify(enc)
        pk = decrypt(settings.SECRET_KEY, _chr)
        return get_user_model().objects.get(pk=pk)

    except DecryptionException:
        logger.warn(u'Payer decryption error')

    except get_user_model().DoesNotExist:
        logger.warn(u'Payer does not exist')


def encode_payer(user):
    """ Кодирование пользователя-инициатора платежа """
    secret = encrypt(settings.SECRET_KEY, six.text_type(user.pk))
    return binascii.hexlify(secret)


def number_generetor(view, form):
    """ Генератор номера платежа (по умолчанию) """
    return u'{:%Y%m%d}-{:08x}'.format(datetime.now(), uuid4().time_low)


def import_class(name):
    return import_string(name)


def get_post_or_get(request):
    """Return the equivalent of request.REQUEST which has been removed in Django 1.9"""
    return request.POST or request.GET


class CSRFExempt(object):
    """ Mixin отключения проверки CSRF ключа """

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(CSRFExempt, self).dispatch(*args, **kwargs)
