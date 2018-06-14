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
)
from openprocurement.caravan.clients import (
    get_contracting_client_with_create_contract,
    get_lots_client,
)
from openprocurement.caravan.observers.lot import (
    LotContractChecker,
)


@attr('internal')
class LotCheckerTest(unittest.TestCase):

    def setUp(self):
        self.db_server, self.db = prepare_db()
        contracting_client = get_contracting_client_with_create_contract()
        self.contract = p_terminated_contract(contracting_client)
        self.lot_id = active_contracting_lot(self.contract.data.id, self.db)

        self.client = get_lots_client()
        self.checker = LotContractChecker(self.client)

        self.message = {
            "lot_id": self.lot_id,
            "contract_id": self.contract.data.id
        }

    def test_check_lot_contract(self):
        lot_contract_from_checker = self.checker._check_lot_contract(self.message)
        assert lot_contract_from_checker.data.id == self.contract.data.id

    def test_prepare_message(self):
        lot_contract_from_api = self.client.get_contract(self.lot_id, self.contract.data.id)
        message = self.checker._prepare_message(lot_contract_from_api, {})
        assert message['lot_contract_status'] is not None

    def test_notify(self):
        lot_from_api = self.client.get_lot(self.lot_id)
        observer = Mock()
        self.checker.register_observer(observer)
        with patch.object(self.checker, '_notify_observers') as mock_notify_observers:
            self.checker.notify(self.message)
            out_payload = mock_notify_observers.call_args_list[0][0][0]
            assert out_payload['lot_id'] == self.lot_id
            assert out_payload['lot_contract_status'] == lot_from_api.data.contracts[0].status
