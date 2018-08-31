# -*- coding: utf-8 -*-
from zope.interface import implementer
from openprocurement.caravan.interfaces import (
    IObservable,
    IObserver,
)
from openprocurement.caravan.log import LOGGER


@implementer(IObservable)
@implementer(IObserver)
class BaseObserverObservable(object):
    """This class implements both IObserver and IObaservable interfaces

    It's not pure implementation of the Observer pattern,
    but it perfectly satisfies this package needs, because
    it allows to construct pipeline of chained classes.
    """

    def __init__(self):
        self._observers = []

    def notify(self, message):
        """Entrypoint of the observer"""
        class_name = self.__class__.__name__
        if self._activate(message):
            LOGGER.info("%s activated", class_name)
            self._run(message)
        else:
            LOGGER.info("%s not activated", class_name)

    def _run(self, message):
        """Holds main code of the observer

        Will be run if the `_activate` method returned `True`.
        """
        raise NotImplementedError

    def _activate(self, message):
        """This method is in charge of observer's activation

        It must to check message, and make decision: to process it or to skip it.
        Returns `True` if the observer must process it.
        Othervise, if message isn't interesting - return `None` or `False`
        """
        raise NotImplementedError

    def register_observer(self, observer):
        self._observers.append(observer)

        observable_name = self.__class__.__name__
        observer_name = observer.__class__.__name__
        LOGGER.info("%s now watches %s", observer_name, observable_name)

    def _notify_observers(self, message):
        emitter_name = self.__class__.__name__
        for observer in self._observers:
            receiver_name = observer.__class__.__name__
            LOGGER.info("%s notifies %s with message %s", emitter_name, receiver_name, message)
            observer.notify(message)


class ObserverObservableWithClient(BaseObserverObservable):
    """Adds `client` attribute to parent class and requires it in the class constructor"""

    def __init__(self, client):
        super(ObserverObservableWithClient, self).__init__()
        self.client = client
