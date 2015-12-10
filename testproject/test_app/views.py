from collections import namedtuple

from django.shortcuts import render


from paymaster.views import InitialView


class NoUserInitialView(InitialView):
    Payer = namedtuple('Payer', 'pk,email,phone')

    def get_user(self, form):
        return self.Payer(*[1, 'test@test.ru', '+7 999 999 99 99'])

