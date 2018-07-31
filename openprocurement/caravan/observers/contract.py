# -*- coding: utf-8 -*-
from openprocurement_client.exceptions import (
    ResourceNotFound,
)
from openprocurement.caravan.observers.base_observer import (
    BaseObserverObservable,
    ObserverObservableWithClient,
)
from openprocurement.caravan.observers.constants import (
    CONTRACT_STATUS_MAPPING,
    PRE_TERMINATED_STATUS_PREFIX,
)
from openprocurement.caravan.observers.errors import (
    CONTRACT_NOT_FOUND,
)
from openprocurement.caravan.utils import (
    LOGGER,
)


class ContractChecker(ObserverObservableWithClient):

    def _activate(self, message):
        if not message.get('error'):
            return True

    def _run(self, message):
        try:
            contract = self._check_contract(message)
        except ResourceNotFound:
            out_message = self._prepare_error_message(CONTRACT_NOT_FOUND, message)
        else:
            out_message = self._prepare_message(contract, message)
        self._notify_observers(out_message)

    def _check_contract(self, message):
        return self.client.get_contract(message['contract_id'])

    def _prepare_message(self, contract, recv_message):
        payload = {
            "contract_id": contract.data.id,
            "contract_status": contract.data.status,
            "lot_id": contract.data.merchandisingObject
        }
        recv_message.update(payload)
        return recv_message

    def _prepare_error_message(self, error, in_message):
        if error == CONTRACT_NOT_FOUND:
            payload = {'error': CONTRACT_NOT_FOUND}
            in_message.update(payload)
        return in_message


class ContractPatcher(ObserverObservableWithClient):

    def _activate(self, message):
        wanted_statuses = CONTRACT_STATUS_MAPPING.keys()
        if (
            not message.get('error')
            and message['contract_status'] in wanted_statuses
        ):
            return True

    def _run(self, message):
        patched_contract = self._patch_contract(message)
        out_message = self._prepare_message(patched_contract, message)
        self._notify_observers(out_message)

    def _patch_contract(self, message):
        target_status = self._get_terminated_status(message['contract_status'])
        contract = self.client.patch_contract(
            message['contract_id'],
            None,
            {'data': {'status': target_status}}
        )
        return contract

    def _prepare_message(self, contract, recv_message):
        payload = {'contract_status': contract.data.status}
        recv_message.update(payload)
        return recv_message

    def _get_terminated_status(self, pre_terminated_status):
        prefix_length = len(PRE_TERMINATED_STATUS_PREFIX)
        return pre_terminated_status[prefix_length:]


class ContractNotFoundHandler(BaseObserverObservable):
    """Handles case of 404 error on contract resource"""

    def _activate(self, message):
        error = message.get('error')
        if error == CONTRACT_NOT_FOUND:
            return True

    def _run(self, message):
        LOGGER.error("Contract {0} not found".format(message['contract_id']))


class ContractAlreadyTerminatedHandler(BaseObserverObservable):

    def _activate(self, message):
        contract_status = message.get('contract_status')
        wanted_statuses = ('terminated', 'unsuccessful')
        if contract_status in wanted_statuses:
            return True

    def _run(self, message):
        LOGGER.info("Contract {0} already terminated".format(message['contract_id']))
