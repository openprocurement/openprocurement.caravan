# -*- coding: utf-8 -*-
from openprocurement.caravan.observers.base_observer import (
    ObserverObservableWithClient,
)
from openprocurement.caravan.constants import (
    CONTRACT_STATUS_MAPPING,
)


class LotContractChecker(ObserverObservableWithClient):
    """Adds lot's status to received message"""

    def _activate(self, message):
        if not message.get('error'):
            return True

    def _run(self, message):
        lot_contract = self._check_lot_contract(message)
        result = self._prepare_message(lot_contract, message)
        self._notify_observers(result)

    def _check_lot_contract(self, message):
        return self.client.get_contract(
            message['lot_id'],
            message['contract_id']
        )

    def _prepare_message(self, lot_contract, recv_message):
        recv_message.update({
            'lot_contract_status': lot_contract.data.status
        })
        return recv_message


class LotContractPatcher(ObserverObservableWithClient):

    def _activate(self, message):
        if not message.get('error'):
            return True

    def _run(self, message):
        lot_conract = self._patch_lot_contract(message)
        out_message = self._prepare_message(lot_conract, message)
        self._notify_observers(out_message)

    def _patch_lot_contract(self, message):
        target_lot_contract_status = CONTRACT_STATUS_MAPPING.get(message['contract_status'])
        contract = self.client.patch_contract(
            message['lot_id'],
            message['contract_id'],
            None,
            {"data": {"status": target_lot_contract_status}}
        )
        return contract

    def _prepare_message(self, lot_contract, recv_message):
        recv_message.update({
            'lot_contract_status': lot_contract.data.status
        })
        return recv_message
