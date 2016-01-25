# -*- coding: utf-8 -*-
import base64
import hashlib
from uuid import uuid4
from datetime import datetime
from simplecrypt import encrypt, decrypt, DecryptionException
from django.utils.importlib import import_module
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from . import settings
from . import logger


def calculate_hash(data, hashed_fields, password=settings.PAYMASTER_PASSWORD, hash_method=None):
    _line = u';'.join(map(str, [data.get(key) for key in hashed_fields]))
    _line += u';{0}'.format(settings.PAYMASTER_PASSWORD)
    hash_method = hash_method or settings.PAYMASTER_HASH_METHOD
    _hash = getattr(hashlib, hash_method)(_line.encode('utf-8'))
    _hash = base64.encodestring(_hash.digest()).replace('\n', '')
    return _hash


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def format_dt(dt):
    return dt.strftime(DATETIME_FORMAT)

def parse_datetime(dt_string):
    from dateutil.parser import parse
    return parse(dt_string)


def decode_payer(enc):
    """ Декодирование пользователя-инициатора платежа """
    try:
        _chr = ''.join(chr(int(enc[i:i + 3])) for i in range(0, len(enc), 3))
        pk = decrypt(settings.SECRET_KEY, _chr)
        return get_user_model().objects.get(pk=pk)

    except DecryptionException:
        logger.warn(u'Payer decryption error')

    except get_user_model().DoesNotExist:
        logger.warn(u'Payer does not exist')


def encode_payer(user):
    """ Кодирование пользователя-инициатора платежа """
    secret = encrypt(settings.SECRET_KEY, unicode(user.pk))
    return u''.join(u'{0:03}'.format(ord(x)) for x in secret)


def number_generetor(view, form):
    """ Генератор номера платежа (по умолчанию) """
    return u'{:%Y%m%d}-{:08x}'.format(datetime.now(), uuid4().get_fields()[0])


def import_class(name):
    module_name, klass_name = name.rsplit('.', 1)
    mod = import_module(module_name)
    klass = getattr(mod, klass_name)
    return klass


class CSRFExempt(object):
    """ Mixin отключения проверки CSRF ключа """

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(CSRFExempt, self).dispatch(*args, **kwargs)
