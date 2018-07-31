# -*- coding: utf-8 -*-
from mock import patch
from nose.plugins.attrib import attr
from openprocurement.caravan.tests.base import (
    CeasefireLokiBaseTest,
)
from openprocurement.caravan.tests.fixtures.contract import (
    p_terminated_contract,
)
from openprocurement.caravan.observers.contract import (
    ContractChecker,
)
from openprocurement.caravan.observers.errors import (
    CONTRACT_NOT_FOUND,
)


@attr('internal')
class ContractCheckerTest(CeasefireLokiBaseTest):

    def setUp(self):
        super(ContractCheckerTest, self).setUp()
        self.p_terminated_contract = p_terminated_contract(self.contracting_client_with_create)

        self.checker = ContractChecker(self.contracting_client)
        self.message = {
            "contract_id": self.p_terminated_contract.data.id,
        }

    def test_notify(self):
        with patch.object(self.checker, '_notify_observers') as mock_notify_observers:
            self.checker.notify(self.message)
            out_message = mock_notify_observers.call_args_list[0][0][0]
            assert out_message['contract_id'] == self.p_terminated_contract.data.id
            assert out_message['lot_id'] == self.p_terminated_contract.data.merchandisingObject
            assert out_message['contract_status'] == self.p_terminated_contract.data.status

    def test_check_contract_ok(self):
        contract = self.checker._check_contract(self.message)
        assert contract.data.id == self.p_terminated_contract.data.id
        assert contract.data.status == self.p_terminated_contract.data.status

    def test_prepare_message(self):
        in_message = {}
        message = self.checker._prepare_message(self.p_terminated_contract, in_message)
        assert message['contract_status'] == 'pending.terminated'
        assert message['contract_id'] == self.p_terminated_contract.data.id
        assert message['lot_id'] == self.p_terminated_contract.data.merchandisingObject

    def test_contract_not_found(self):
        self.message['contract_id'] = "074d43928e36414487fc2a41d53cb5ba"  # unreal ID
        with patch.object(self.checker, '_notify_observers') as mock_notify_observers:
            self.checker.notify(self.message)
            out_message = mock_notify_observers.call_args_list[0][0][0]
            assert out_message['error'] == CONTRACT_NOT_FOUND

    def test_contract_already_terminated(self):
        self.contracting_client.patch_contract(
            self.message['contract_id'],
            None,
            {'data': {'status': 'terminated'}}
        )
        with patch.object(self.checker, '_notify_observers') as mock_notify_observers:
            self.checker.notify(self.message)
            out_message = mock_notify_observers.call_args_list[0][0][0]
            assert out_message['contract_status'] == 'terminated'
