# -*- coding: utf-8 -*-
from zope.interface import Interface


class IDBWatcher(Interface):

    def update(self):
        """Update watcher's found items"""
        pass

    def get(self):
        """Get an id, that watcher had captured"""
        pass
