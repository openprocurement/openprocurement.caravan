# -*- coding: utf-8 -*-
from nose.plugins.attrib import attr

from openprocurement.caravan.tests.base import CeasefireLokiBaseTest
from openprocurement.caravan import utils
from openprocurement.caravan.watchers.contracts_watcher import (
    ContractsDBWatcher,
)
from openprocurement.caravan.tests.fixtures.contract import (
    p_terminated_contract,
    p_unsuccessful_contract,
)


@attr('internal')
class WatcherUpdateTest(CeasefireLokiBaseTest):

    def setUp(self):
        super(WatcherUpdateTest, self).setUp()
        p_terminated_contract(self.contracting_client_with_create)
        p_unsuccessful_contract(self.contracting_client_with_create)

    def test_update_ok(self):
        cw = ContractsDBWatcher(self.db)
        found_items_count = cw.update()
        assert found_items_count >= 2

    def test_update_when_not_empty(self):
        cw = ContractsDBWatcher(self.db)
        found_items_count = cw.update()
        cw.get()  # remove one result
        found_items_count_after_update = cw.update()
        assert found_items_count_after_update == found_items_count - 1
