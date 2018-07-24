# -*- coding: utf-8 -*-
import unittest
from mock import patch, Mock
from nose.plugins.attrib import attr

from openprocurement.caravan.tests.fixtures.lot import (
    active_contracting_lot,
)
from openprocurement.caravan.utils import (
    prepare_db,
)
from openprocurement.caravan.tests.fixtures.contract import (
    p_terminated_contract,
    interconnect_contract_with_lot,
)
from openprocurement.caravan.clients import (
    get_contracting_client_with_create_contract,
    get_lots_client,
)
from openprocurement.caravan.observers.lot import (
    LotContractPatcher,
)


@attr('internal')
class LotContractPatcherTest(unittest.TestCase):

    def setUp(self):
        self.db_server, self.db = prepare_db()
        contracting_client = get_contracting_client_with_create_contract()
        self.contract = p_terminated_contract(contracting_client)
        self.lots_client = get_lots_client()
        self.lot_id = active_contracting_lot(self.contract.data.id, self.db)
        lot_contract_id = interconnect_contract_with_lot(self.contract.data.id, self.lot_id, self.db)

        self.client = get_lots_client()
        self.patcher = LotContractPatcher(self.client)

        self.message = {
            "lot_id": self.lot_id,
            "contract_id": self.contract.data.id,
            "contract_status": self.contract.data.status,
            "lot_contract_status": "scheduled",
            "lot_contract_id": lot_contract_id
        }

    def test_patch_lot_contract_to_complete(self):
        contract = self.patcher._patch_lot_contract(self.message)
        assert contract.data.status == 'complete'
        lot_from_api_after_contract_patch = self.client.get_lot(self.lot_id)
        assert lot_from_api_after_contract_patch.data.status == 'pending.sold'

    def test_prepare_message(self):
        lot_contract = Mock()
        lot_contract.data.status = 'complete'
        message = self.patcher._prepare_message(lot_contract, {})
        assert message['lot_contract_status'] == lot_contract.data.status

    def test_notify(self):
        observer = Mock()
        self.patcher.register_observer(observer)
        with patch.object(self.patcher, '_notify_observers') as mock_notify_observers:
            self.patcher.notify(self.message)
            out_payload = mock_notify_observers.call_args_list[0][0][0]
            assert out_payload['lot_contract_status'] in ('complete', 'unsuccessful')
