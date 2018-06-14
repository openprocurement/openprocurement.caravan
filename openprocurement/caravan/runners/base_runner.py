# -*- coding: utf-8 -*-
from openprocurement.caravan.runners.killer import (
    GracefulKiller,
)


class BaseRunner(object):

    def __init__(self):
        self.killer = GracefulKiller()
