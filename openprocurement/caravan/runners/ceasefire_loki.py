# -*- coding: utf-8 -*-
from time import sleep
from random import randint

from openprocurement.caravan.utils import (
    connect_to_db,
    parse_args,
)
from openprocurement.caravan.config import app_config
from openprocurement.caravan.watchers.contracts_watcher import (
    ContractsDBWatcher,
)
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
from openprocurement.caravan.runners.base_runner import (
    BaseRunner,
)
from openprocurement_client.resources.contracts import (
    ContractingClient,
)
from openprocurement_client.resources.lots import (
    LotsClient,
)


class CeasefireLokiRunner(BaseRunner):

    def __init__(self, ceasefire_db, ceasefire_client, loki_client, sleep_time_range):
        """Runner init and observers interconnection

        It's complicated, so you're welcome to see explanatory diagram in
        `docs/caravan.xml` on draw.io

        :param sleep_time_range: tuple with min and max sleep time in seconds like (1, 10)
        """
        super(CeasefireLokiRunner, self).__init__()

        self.sleep_time_range = sleep_time_range

        # init db watcher
        self.db_watcher = ContractsDBWatcher(ceasefire_db)

        # init observers
        contract_checker = ContractChecker(ceasefire_client)
        contract_patcher = ContractPatcher(ceasefire_client)
        contract_already_terminated_handler = ContractAlreadyTerminatedHandler()
        contract_not_found_handler = ContractNotFoundHandler()

        lot_contract_checker = LotContractChecker(loki_client)
        lot_contract_patcher = LotContractPatcher(loki_client)
        lot_contract_already_complete_handler = LotContractAlreadyCompleteHandler()
        lot_contract_not_found_handler = LotContractNotFoundHandler()

        # connect observers
        # base flow
        contract_checker.register_observer(lot_contract_checker)
        lot_contract_checker.register_observer(lot_contract_patcher)
        lot_contract_patcher.register_observer(contract_patcher)
        # handlers
        contract_checker.register_observer(contract_already_terminated_handler)
        contract_checker.register_observer(contract_not_found_handler)

        lot_contract_checker.register_observer(lot_contract_already_complete_handler)
        lot_contract_checker.register_observer(lot_contract_not_found_handler)

        self.first_observer = contract_checker

    def _sync_one_watchers_queue(self):
        found_contracts_count = self.db_watcher.update()
        for _ in xrange(found_contracts_count):
            contract_id = self.db_watcher.get()
            self.first_observer.notify({'contract_id': contract_id})

    def start(self):
        while not self.killer.kill:
            self._sync_one_watchers_queue()
            sleep(randint(*self.sleep_time_range))


def main():
    args = parse_args()
    config = app_config(args.config)

    db = connect_to_db(
        config.contracting.db.protocol,
        config.contracting.db.host,
        config.contracting.db.port,
        config.contracting.db.name
    )

    ceasefire_client = ContractingClient(
        host_url=config.contracting.api.host,
        api_version=config.contracting.api.version,
        key=config.contracting.api.token,
    )

    loki_client = LotsClient(
        host_url=config.lots.api.host,
        api_version=config.lots.api.version,
        key=config.lots.api.token,
    )

    sleep_time_range = (
        config.runner.sleep_seconds.min,
        config.runner.sleep_seconds.max
    )

    import ipdb; ipdb.set_trace()
    runner = CeasefireLokiRunner(db, ceasefire_client, loki_client, sleep_time_range)

    runner.start()
