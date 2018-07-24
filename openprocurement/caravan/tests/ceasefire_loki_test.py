# -*- coding: utf-8 -*-
from unittest import TestCase
from nose.plugins.attrib import attr

from openprocurement.caravan.runners.ceasefire_loki import CeasefireLokiRunner

from openprocurement.caravan.utils import prepare_db, clean_db
from openprocurement.caravan.clients import (
    get_contracting_client,
    get_contracting_client_with_create_contract,
    get_lots_client,
)
from openprocurement.caravan.tests.fixtures.contract import (
    interconnect_contract_with_lot,
    p_terminated_contract,
)
from openprocurement.caravan.tests.fixtures.lot import (
    active_contracting_lot,
)


@attr('internal')
class CeasefireLokiTest(TestCase):

    def setUp(self):
        self.db_server, self.db = prepare_db()
        clean_db(self.db)  # db must not have contracts without real lots related
        client_with_create = get_contracting_client_with_create_contract()
        self.pt_contract = p_terminated_contract(client_with_create)
        self.contracting_client = get_contracting_client()
        self.lots_client = get_lots_client()
        self.lot_id = active_contracting_lot(self.pt_contract.data.id, self.db)

        # fixtures must be pointing each other
        interconnect_contract_with_lot(self.pt_contract.data.id, self.lot_id, self.db)

        self.runner = CeasefireLokiRunner(self.db, self.contracting_client, self.lots_client)

    def test_general_terminate_contract(self):
        self.runner._sync_one_watchers_queue()

        patched_contract = self.contracting_client.get_contract(self.pt_contract.data.id)
        assert patched_contract.data.status == 'terminated'
