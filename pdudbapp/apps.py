# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class PdudbappConfig(AppConfig):
    name = 'pdudbapp'
    
    def ready(self):
        import pdudbapp.signals  #registra la señal
