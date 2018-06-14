# -*- coding: utf-8 -*-
from copy import deepcopy

from openprocurement.caravan.tests.fixtures.lot_data import (
    raw_active_contracting_lot,
)


def _set_contract_id(contract_id, data):
    data['contracts'][0].update({'id': contract_id})
    return data


def raw_lot_fixture(**kwargs):
    contract_id = kwargs.get('contract_id')

    fixture = deepcopy(raw_active_contracting_lot)
    if contract_id:
        fixture = _set_contract_id(contract_id, fixture)

    return fixture


def active_contracting_lot(contract_id, db):
    lot_data = raw_lot_fixture(contract_id=contract_id)
    doc_id, _ = db.save(lot_data)
    return doc_id
