# -*- coding: utf-8 -*-
from zope.interface import (
    Interface,
)


class IObservable(Interface):

    def register_observer(self, observer):
        pass


class IObserver(Interface):

    def notify(self, message):
        pass
