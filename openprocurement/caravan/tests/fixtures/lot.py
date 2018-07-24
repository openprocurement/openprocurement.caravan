# -*- coding: utf-8 -*-
from copy import deepcopy

from openprocurement.caravan.tests.fixtures.lot_data import (
    raw_active_contracting_lot,
)


def raw_lot_fixture():
    fixture = deepcopy(raw_active_contracting_lot)
    return fixture


def active_contracting_lot(contract_id, db):
    lot_data = raw_lot_fixture()
    doc_id, _ = db.save(lot_data)
    return doc_id
