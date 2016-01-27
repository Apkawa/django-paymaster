# coding: utf-8
from __future__ import unicode_literals

from django.utils.encoding import smart_str


class APIError(Exception):
    message = 'Неизвестная ошибка. Сбой в системе PayMaster. Если ошибка повторяется, обратитесь в техподдержку.'
    code = -1

    def __unicode__(self):
        return "({self.code}) {self.message}".format(self=self)

    def __str__(self):
        return smart_str(self.__unicode__())


class NetworkError(APIError):
    message = 'Сетевая ошибка. Сбой в системе PayMaster. Если ошибка повторяется, обратитесь в техподдержку.'
    code = -2


class PermissionError(APIError):
    message = 'Нет доступа. Неверно указан логин, или у данного логина нет прав на запрошенную информацию.'
    code = -6


class SignError(APIError):
    message = 'Неверная подпись запроса. Неверно сформирован хеш запроса.'
    code = -7


class PaymentNotFound(APIError):
    message = 'Платеж не найден по номеру счета'
    code = -13


class DuplicateNonce(APIError):
    message = 'Повторный запрос с тем же nonce'
    code = -14


class UncorrectAmountValue(APIError):
    message = 'Неверное значение суммы (в случае возвратов имеется в виду значение amount)'
    code = -18


PAYMASTER_ERROR_CODES = {e.code: e for e in
                         [
                             APIError,
                             NetworkError,
                             PermissionError,
                             SignError,
                             PaymentNotFound,
                             DuplicateNonce,
                             UncorrectAmountValue
                         ]
                         }
