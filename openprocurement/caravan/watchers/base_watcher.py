# -*- coding: utf-8 -*-
from Queue import (
    Empty,
    Queue,
)
from zope.interface import implementer

from openprocurement.caravan.watchers.constants import (
    WATCHER_IDS_QUEUE_MAX_SIZE,
)
from openprocurement.caravan.watchers.interfaces import (
    IDBWatcher,
)


@implementer(IDBWatcher)
class BaseDBWatcher(object):

    def __init__(self, db):
        self._ids = Queue(maxsize=WATCHER_IDS_QUEUE_MAX_SIZE)
        self._db = db

    def update(self):
        raise NotImplementedError

    def get(self):
        try:
            return self._ids.get_nowait()
        except Empty:
            return None
