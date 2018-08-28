# -*- coding: utf-8 -*-
from mock import patch
from nose.plugins.attrib import attr

from openprocurement.caravan.tests.base import CeasefireLokiBaseTest
from openprocurement.caravan.observers.contract import (
    ContractAlreadyTerminatedHandler,
    ContractChecker,
    ContractNotFoundHandler,
    ContractPatcher,
)
from openprocurement.caravan.observers.lot import (
    LotContractAlreadyCompleteHandler,
    LotContractChecker,
    LotContractNotFoundHandler,
    LotContractPatcher,
)
from openprocurement.caravan.tests.fixtures.contract import (
    p_terminated_contract,
    p_unsuccessful_contract,
    interconnect_contract_with_lot,
)
from openprocurement.caravan.tests.fixtures.lot import (
    active_contracting_lot,
)


@attr('internal')
class ContractCheckerContractNotFoundHandlerTest(CeasefireLokiBaseTest):

    def setUp(self):
        super(ContractCheckerContractNotFoundHandlerTest, self).setUp()
        self.checker = ContractChecker(self.contracting_client)
        self.message = {
            "contract_id": "074d43928e36414487fc2a41d53cb5ba"  # unreal ID
        }
        self.checker = ContractChecker(self.contracting_client)
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


@attr('internal')
class ContractCheckerWhenContractAlreadyPatched(CeasefireLokiBaseTest):

    def setUp(self):
        super(ContractCheckerWhenContractAlreadyPatched, self).setUp()
        self.p_terminated_contract = p_terminated_contract(self.contracting_client_with_create, dockey=self.dockey)

        self.checker = ContractChecker(self.contracting_client)
        not_found_handler = ContractNotFoundHandler()
        ready_contract_handler = ContractAlreadyTerminatedHandler()
        self.checker.register_observer(not_found_handler)
        self.checker.register_observer(ready_contract_handler)
        self.message = {
            "contract_id": self.p_terminated_contract.data.id,
        }

    @patch('openprocurement.caravan.observers.contract.LOGGER')
    def test_ok(self, logger):
        self.contracting_client.patch_contract(
            self.message['contract_id'],
            None,
            {'data': {'status': 'terminated'}}
        )
        self.checker.notify(self.message)
        log_message = logger.info.call_args_list[1][0][0]
        assert 'already terminated' in log_message


@attr('internal')
class LotContractCheckerLotContractAlreadyCompleteHandlerTest(CeasefireLokiBaseTest):

    def setUp(self):
        super(LotContractCheckerLotContractAlreadyCompleteHandlerTest, self).setUp()
        self.contract = p_unsuccessful_contract(self.contracting_client_with_create)
        self.lot_id = active_contracting_lot(self.contract.data.id, self.db)
        lot_contract_id = interconnect_contract_with_lot(self.contract.data.id, self.lot_id, self.db)

        self.message = {
            "lot_id": self.lot_id,
            "contract_id": self.contract.data.id,
            "contract_status": self.contract.data.status,
            "lot_contract_id": lot_contract_id,
        }

        self.checker = LotContractChecker(self.lots_client)
        self.lots_patcher = LotContractPatcher(self.lots_client)
        contracts_patcher = ContractPatcher(self.contracting_client)
        lot_contract_completed_handler = LotContractAlreadyCompleteHandler()

        self.checker.register_observer(self.lots_patcher)
        self.lots_patcher.register_observer(contracts_patcher)
        self.checker.register_observer(lot_contract_completed_handler)
        lot_contract_completed_handler.register_observer(contracts_patcher)

        self.lots_client.patch_contract(
            self.message['lot_id'],
            self.message['lot_contract_id'],
            None,
            {'data': {'status': 'unsuccessful'}}
        )

    def test_ok(self):
        with patch.object(self.lots_patcher, '_run') as mocked_patcher_run:
            self.checker.notify(self.message)
            patched_contract = self.contracting_client.get_contract(self.contract.data.id)
            assert patched_contract.data.status == 'unsuccessful'
            assert len(mocked_patcher_run.call_args_list) == 0  # assert that lot patcher didn't run


@attr('internal')
class LotContractNotFoundHandlerTest(CeasefireLokiBaseTest):

    def setUp(self):
        super(LotContractNotFoundHandlerTest, self).setUp()
        self.lot_checker = LotContractChecker(self.lots_client)
        self.lot_patcher = LotContractPatcher(self.lots_client)
        self.lot_contract_not_found_handler = LotContractNotFoundHandler()

        self.lot_checker.register_observer(self.lot_patcher)
        self.lot_checker.register_observer(self.lot_contract_not_found_handler)

        # fake ids to get 404
        self.message = {
            "contract_id": "70f301efd09c4240a5453de656fcc68b",
            "lot_id": "1cf7be90a0554754ac5c3ebdf5d6e5c2",
            "lot_contract_id": "65559cacb9f9476a97f6c5ae001c58f7",
        }

    @patch('openprocurement.caravan.observers.lot.LOGGER')
    def test_ok(self, logger):
        self.lot_checker.notify(self.message)
        log_message = logger.error.call_args_list[0][0][0]
        assert self.message['lot_id'] in log_message
        assert self.message['lot_contract_id'] in log_message
        assert 'not found' in log_message

    def test_lot_patcher_not_run(self):
        with patch.object(self.lot_patcher, '_run') as run:
            self.lot_checker.notify(self.message)
            assert len(run.call_args_list) == 0  # prove that `_run` isn't called
