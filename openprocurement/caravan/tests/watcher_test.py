# -*- coding: utf-8 -*-
import unittest

from nose.plugins.attrib import attr
from openprocurement.caravan import utils
from openprocurement.caravan.watchers.contracts_watcher import (
    ContractsDBWatcher,
)
from openprocurement.caravan.tests.fixtures.contract import (
    p_terminated_contract,
    p_unsuccessful_contract,
)
from openprocurement.caravan.clients import (
    get_contracting_client_with_create_contract,
)


@attr('internal')
class WatcherUpdateTest(unittest.TestCase):

    def setUp(self):
        self.db_server, self.db = utils.prepare_db()
        client_with_create = get_contracting_client_with_create_contract()
        p_terminated_contract(client_with_create)
        p_unsuccessful_contract(client_with_create)

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
