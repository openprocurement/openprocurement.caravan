# -*- coding: utf-8 -*-
import sys
from time import sleep
from retrying import retry

from openprocurement.caravan.watchers.contracts_watcher import (
    ContractsDBWatcher,
)
from openprocurement.caravan.observers.contract import (
    ContractChecker,
    ContractPatcher,
)
from openprocurement.caravan.observers.lot import (
    LotContractChecker,
    LotContractPatcher,
)
from openprocurement.caravan.runners.base_runner import (
    BaseRunner,
)
from openprocurement.caravan.utils import get_sleep_time


class CeasefireLokiRunner(BaseRunner):

    def __init__(self, ceasefire_db, ceasefire_client, loki_client):
        super(CeasefireLokiRunner, self).__init__()

        # init db watcher
        self.db_watcher = ContractsDBWatcher(ceasefire_db)

        # init observers
        contract_checker = ContractChecker(ceasefire_client)
        lot_contract_checker = LotContractChecker(loki_client)
        lot_contract_patcher = LotContractPatcher(loki_client)
        contract_patcher = ContractPatcher(ceasefire_client)

        # connect observers
        contract_checker.register_observer(lot_contract_checker)
        lot_contract_checker.register_observer(lot_contract_patcher)
        lot_contract_patcher.register_observer(contract_patcher)

        self.first_observer = contract_checker

    def _sync_one_watchers_queue(self):
        found_contracts_count = self.db_watcher.update()
        for _ in xrange(found_contracts_count):
            contract_id = self.db_watcher.get()
            self.first_observer.notify({'contract_id': contract_id})

    def start(self):
        while not self.killer.kill:
            self._sync_one_watchers_queue()
            sleep(get_sleep_time())
