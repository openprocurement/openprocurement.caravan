# -*- coding: utf-8 -*-
import iso8601

from copy import deepcopy
from datetime import timedelta
from openprocurement.api.tests.helpers import (
    fake_docservice_url,
)
from openprocurement.caravan.tests.constants import (
    MILESTONE_TYPES_NEED_DOCUMENT_TO_MET,
)
from openprocurement.api.utils.searchers import (
    search_list_with_dicts,
)
from openprocurement.caravan.tests.fixtures.contract_data import (
    contract_create_data,
)
from openprocurement.caravan.tests.fixtures.document_data import (
    test_document_data,
)


def create_contract(client, data=None):
    """Create contract as it could be created by bridge"""
    if data is None:
        data = contract_create_data
    return client.create_contract(data)


def upload_document_to_milestone(contract_id, milestone_id, token, client, dockey, **kwargs):
    doc_url = fake_docservice_url(dockey)
    doc_data = deepcopy(test_document_data)
    doc_data.update({
        'relatedItem': milestone_id,
        'documentOf': 'milestone',
        'url': doc_url
    })
    if kwargs.get('data'):
        doc_data.update(kwargs['data'])
    wrapped_data = {'data': doc_data}
    client.post_document(contract_id, token, wrapped_data)


def make_milestone_met(contract_id, milestone_id, token, client, **kwargs):
    contract = client.get_contract(contract_id)
    target_milestone = search_list_with_dicts(
        contract.data.milestones,
        'id',
        milestone_id
    )
    if target_milestone.type in MILESTONE_TYPES_NEED_DOCUMENT_TO_MET:
        upload_document_to_milestone(
            contract_id,
            milestone_id,
            token,
            client,
            kwargs['dockey'],
        )
    due_date = iso8601.parse_date(target_milestone.dueDate)
    date_met = due_date - timedelta(days=1)
    client.patch_milestone(
        contract_id,
        milestone_id,
        token,
        {"data": {"dateMet": date_met.isoformat()}}
    )


def active_payment_contract(contract_id, token, client):
    return client.patch_contract(
        contract_id,
        token,
        {'data': {'status': 'active.payment'}}
    )


def p_terminated_contract(client, **kwargs):
    create_response = create_contract(client)
    contract_id = create_response.data.id
    token = create_response.access.token

    response = active_payment_contract(contract_id, token, client)
    for milestone in response.data.milestones:
        make_milestone_met(contract_id, milestone.id, token, client, dockey=kwargs['dockey'])
    return client.get_contract(contract_id)


def p_unsuccessful_contract(client):
    create_response = create_contract(client)
    contract_id = create_response.data.id
    token = create_response.access.token

    response = active_payment_contract(contract_id, token, client)
    client.patch_milestone(
        contract_id,
        response.data.milestones[0].id,
        token,
        {'data': {'status': 'notMet'}}
    )
    return client.get_contract(contract_id)


def interconnect_contract_with_lot(contract_id, lot_id, db):
    contract = db[contract_id]
    lot = db[lot_id]

    lot['contracts'][0]['relatedProcessID'] = contract_id
    db.save(lot)

    contract['merchandisingObject'] = lot_id
    db.save(contract)
    return lot['contracts'][0]['id']
