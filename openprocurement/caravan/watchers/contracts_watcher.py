# -*- coding: utf-8 -*-
from couchdb.design import ViewDefinition

from openprocurement.caravan.watchers.constants import (
    WATCHER_IDS_QUEUE_MAX_SIZE,
)
from openprocurement.caravan.watchers.base_watcher import BaseDBWatcher


class ContractsDBWatcher(BaseDBWatcher):

    def __init__(self, db):
        super(ContractsDBWatcher, self).__init__(db)
        self._db_view = self._init_terminal_contracts_view()

    def update(self):
        items_count = self._ids.qsize()
        if items_count > 0:  # no actual update while internal container isn't empty
            return items_count

        view_result = self._db_view(self._db, limit=WATCHER_IDS_QUEUE_MAX_SIZE)
        for row in view_result.rows:
            self._ids.put(row.id)

        return self._ids.qsize()

    def _init_terminal_contracts_view(self):
        terminal_contracts_view = ViewDefinition(
            'contract_views',
            'has_terminal_status',
            '''function(doc) {
                if (doc.status == 'pending.terminated' || doc.status == 'pending.unsuccessful') {
                    emit(doc._id, doc.status);
                }
            }
            '''
        )
        terminal_contracts_view.sync(self._db)
        return terminal_contracts_view
