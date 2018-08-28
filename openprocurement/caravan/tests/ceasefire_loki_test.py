# -*- coding: utf-8 -*-
from nose.plugins.attrib import attr

from openprocurement.caravan.tests.base import CeasefireLokiBaseTest
from openprocurement.caravan.runners.ceasefire_loki import CeasefireLokiRunner

from openprocurement.caravan.utils import clean_db
from openprocurement.caravan.tests.fixtures.contract import (
    interconnect_contract_with_lot,
    p_terminated_contract,
)
from openprocurement.caravan.tests.fixtures.lot import (
    active_contracting_lot,
)


@attr('internal')
class CeasefireLokiTest(CeasefireLokiBaseTest):

    def setUp(self):
        super(CeasefireLokiTest, self).setUp()

        clean_db(self.db)  # db must not have contracts without real lots related
        self.pt_contract = p_terminated_contract(self.contracting_client_with_create, dockey=self.dockey)
        self.lot_id = active_contracting_lot(self.pt_contract.data.id, self.db)

        # fixtures must be pointing each other
        interconnect_contract_with_lot(self.pt_contract.data.id, self.lot_id, self.db)

        sleep_time_range = (
            self.config.runner.sleep_seconds.min,
            self.config.runner.sleep_seconds.max
        )
        self.runner = CeasefireLokiRunner(
            self.db, self.contracting_client, self.lots_client, sleep_time_range
        )

    def test_general_terminate_contract(self):
        self.runner._sync_one_watchers_queue()

        patched_contract = self.contracting_client.get_contract(self.pt_contract.data.id)
        assert patched_contract.data.status == 'terminated'
