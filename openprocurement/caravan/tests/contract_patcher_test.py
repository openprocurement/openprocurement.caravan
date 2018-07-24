# -*- coding: utf-8 -*-
import unittest
from mock import patch
from nose.plugins.attrib import attr

from openprocurement.caravan.tests.fixtures.contract import (
    p_terminated_contract,
)
from openprocurement.caravan.clients import (
    get_contracting_client,
    get_contracting_client_with_create_contract,
)
from openprocurement.caravan.observers.contract import (
    ContractPatcher,
)


@attr('internal')
class ContractPatcherTest(unittest.TestCase):

    def setUp(self):
        client_with_create_permission = get_contracting_client_with_create_contract()
        self.p_terminated_contract = p_terminated_contract(client_with_create_permission)

        self.client = get_contracting_client()
        self.patcher = ContractPatcher(self.client)

        self.message = {
            "contract_id": self.p_terminated_contract.data.id,
            "contract_status": self.p_terminated_contract.data.status,
        }

    def test_get_terminated_status(self):
        test_statuses = {
            "pending.terminated": "terminated",
            "pending.unsuccessful": "unsuccessful",
        }
        for pre_terminated, terminated in test_statuses.iteritems():
            assert self.patcher._get_terminated_status(pre_terminated) == terminated

    def test_patch_contract_to_terminated(self):
        patched_contract = self.patcher._patch_contract(self.message)
        assert patched_contract.data.status == 'terminated'

    def test_prepare_message(self):
        message = {}
        self.patcher._prepare_message(self.p_terminated_contract, message)
        assert message['contract_status'] == 'pending.terminated'

    def test_notify(self):
        with patch.object(self.patcher, '_notify_observers') as mock_notify_observers:
            self.patcher.notify(self.message)
            out_message = mock_notify_observers.call_args_list[0][0][0]
            assert out_message['contract_status'] == 'terminated'
