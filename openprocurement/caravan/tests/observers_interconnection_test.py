# -*- coding: utf-8 -*-
from unittest import TestCase
from mock import patch

from openprocurement.caravan.clients import (
    get_contracting_client,
    get_contracting_client_with_create_contract,
    get_lots_client,
)
from openprocurement.caravan.observers.contract import (
    ContractChecker,
    ContractNotFoundHandler,
    ContractAlreadyTerminatedHandler,
)
from openprocurement.caravan.observers.lot import (
    LotContractChecker,
)
from openprocurement.caravan.tests.fixtures.contract import (
    p_terminated_contract,
)


class ContractCheckerContractNotFoundHandlerTest(TestCase):

    def setUp(self):
        self.client = get_contracting_client()
        self.lots_client = get_lots_client()
        self.checker = ContractChecker(self.client)
        self.message = {
            "contract_id": "074d43928e36414487fc2a41d53cb5ba"  # unreal ID
        }
        self.checker = ContractChecker(self.client)
        not_found_handler = ContractNotFoundHandler()
        lot_checker = LotContractChecker(self.lots_client)
        self.checker.register_observer(not_found_handler)
        self.checker.register_observer(lot_checker)

    @patch('openprocurement.caravan.observers.contract.LOGGER')
    def test_ok(self, logger):
        self.checker.notify(self.message)
        log_message = logger.error.call_args_list[0][0][0]
        assert self.message['contract_id'] in log_message
        assert 'not found' in log_message


class ContractCheckerWhenContractAlreadyPatched(TestCase):

    def setUp(self):
        client_with_create_permission = get_contracting_client_with_create_contract()
        self.p_terminated_contract = p_terminated_contract(client_with_create_permission)

        self.client = get_contracting_client()
        self.checker = ContractChecker(self.client)
        not_found_handler = ContractNotFoundHandler()
        ready_contract_handler = ContractAlreadyTerminatedHandler()
        self.checker.register_observer(not_found_handler)
        self.checker.register_observer(ready_contract_handler)
        self.message = {
            "contract_id": self.p_terminated_contract.data.id,
        }

    @patch('openprocurement.caravan.observers.contract.LOGGER')
    def test_ok(self, logger):
        self.client.patch_contract(
            self.message['contract_id'],
            None,
            {'data': {'status': 'terminated'}}
        )
        self.checker.notify(self.message)
        log_message = logger.info.call_args_list[0][0][0]
        assert 'already terminated' in log_message


class LotContractCheckerLotContractAlreadyInCompleteStatusTest(TestCase):
    pass
