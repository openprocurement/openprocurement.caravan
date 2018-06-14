# -*- coding: utf-8 -*-
import iso8601

from datetime import timedelta
from openprocurement.caravan.utils import (
    search_list_with_dicts,
)
from openprocurement.caravan.tests.fixtures.contract_data import (
    contract_create_data,
)


def create_contract(client, data=None):
    """Create contract as it could be created by bridge"""
    if data is None:
        data = contract_create_data
    return client.create_contract(data)


def make_milestone_met(contract_id, milestone_id, token, client):
    contract = client.get_contract(contract_id)
    target_milestone = search_list_with_dicts(
        contract.data.milestones,
        'id',
        milestone_id
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


def p_terminated_contract(client):
    create_response = create_contract(client)
    contract_id = create_response.data.id
    token = create_response.access.token

    response = active_payment_contract(contract_id, token, client)
    for milestone in response.data.milestones:
        make_milestone_met(contract_id, milestone.id, token, client)
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

    lot['contracts'][0]['id'] = contract_id
    db.save(lot)

    contract['merchandisingObject'] = lot_id
    db.save(contract)
