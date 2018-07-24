# -*- coding: utf-8 -*-
from openprocurement_client.exceptions import (
    ResourceNotFound,
)
from openprocurement.caravan.observers.base_observer import (
    BaseObserverObservable,
    ObserverObservableWithClient,
)
from openprocurement.caravan.constants import (
    CONTRACT_STATUS_MAPPING,
    LOT_CONTRACT_TERMINAL_STATUSES,
)
from openprocurement.caravan.utils import (
    LOGGER,
    search_lot_contract_by_related_contract,
)
from openprocurement.caravan.observers.errors import (
    LOT_CONTRACT_NOT_FOUND,
)


class LotContractChecker(ObserverObservableWithClient):
    """Adds lot's status to received message"""

    def _activate(self, message):
        if not message.get('error'):
            return True

    def _run(self, message):
        try:
            lot_contract = self._check_lot_contract(message)
        except ResourceNotFound:
            result = self._prepare_error_message(LOT_CONTRACT_NOT_FOUND, message)
        else:
            result = self._prepare_message(lot_contract, message)
        self._notify_observers(result)

    def _check_lot_contract(self, message):
        return search_lot_contract_by_related_contract(
            self.client,
            message['lot_id'],
            message['contract_id']
        )

    def _prepare_message(self, lot_contract, recv_message):
        recv_message.update({
            'lot_contract_status': lot_contract.status,
            'lot_contract_id': lot_contract.id
        })
        return recv_message

    def _prepare_error_message(self, error, in_message):
        if error == LOT_CONTRACT_NOT_FOUND:
            in_message.update({'error': LOT_CONTRACT_NOT_FOUND})
            return in_message


class LotContractPatcher(ObserverObservableWithClient):

    def _activate(self, message):
        if (
            not message.get('error')
            and not (message['lot_contract_status'] in LOT_CONTRACT_TERMINAL_STATUSES)  # skip already finished contracts
        ):
            return True

    def _run(self, message):
        lot_conract = self._patch_lot_contract(message)
        out_message = self._prepare_message(lot_conract, message)
        self._notify_observers(out_message)

    def _patch_lot_contract(self, message):
        target_lot_contract_status = CONTRACT_STATUS_MAPPING.get(message['contract_status'])
        contract = self.client.patch_contract(
            message['lot_id'],
            message['lot_contract_id'],
            None,
            {"data": {"status": target_lot_contract_status}}
        )
        return contract

    def _prepare_message(self, lot_contract, recv_message):
        recv_message.update({
            'lot_contract_status': lot_contract.data.status
        })
        return recv_message


class LotContractAlreadyCompleteHandler(BaseObserverObservable):

    def _activate(self, message):
        if (
            message['lot_contract_status'] in LOT_CONTRACT_TERMINAL_STATUSES
        ):
            return True

    def _run(self, message):
        LOGGER.info(
            'Contract {0} of lot {1} is already in terminal status'.format(
                message['lot_contract_id'],
                message['lot_id']
            )
        )
        self._notify_observers(message)


class LotContractNotFoundHandler(BaseObserverObservable):

    def _activate(self, message):
        if (
            message.get('error') == LOT_CONTRACT_NOT_FOUND
        ):
            return True

    def _run(self, message):
        LOGGER.error(
            "Lot {0} or some it's subresource {1} not found".format(
                message['lot_id'],
                message['lot_contract_id']))
