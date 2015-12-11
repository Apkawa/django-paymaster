# coding: utf-8
from __future__ import unicode_literals

import base64
import json

from django.contrib.auth import get_user_model
from simplecrypt import encrypt, decrypt, DecryptionException

from . import logger
from . import settings


class AbstractPayerEncoder(object):
    """
    Абстрактный класс кодирования и декодирования объекта плательщика

    """

    def get_sercet_key(self):
        return settings.SECRET_KEY

    def serialize_data(self, data):
        """
        :param data:
        :return:
        """
        return json.dumps(data)

    def deserialize_data(self, serialized_data):
        return json.loads(serialized_data)

    def decode_data(self, enc):
        try:
            data = decrypt(settings.SECRET_KEY, base64.decodestring(enc))
            return self.deserialize_data(data)
        except DecryptionException:
            logger.warn(u'Payer decryption error')

        except get_user_model().DoesNotExist:
            logger.warn(u'Payer does not exist')

    def encode_data(self, data):
        secret = encrypt(settings.SECRET_KEY, self.serialize_data(data))
        return base64.encodestring(secret)

    def encode(self, *args, **kwargs):
        raise NotImplemented()

    def decode(self, encoded_data):
        raise NotImplemented()


class PayerEncoder(AbstractPayerEncoder):
    def encode(self, payer):
        return self.encode_data({"pk": payer.pk})

    def decode(self, encoded_data):
        data = self.decode_data(encoded_data)
        return get_user_model().get(pk=data.pk)


class RawPayerEncoder(AbstractPayerEncoder):
    def encode(self, data):
        return self.encode_data(data)

    def decode(self, encoded_data):
        return self.decode_data(encoded_data)
