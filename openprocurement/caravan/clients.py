# -*- coding: utf-8 -*-
from openprocurement_client.resources.contracts import (
    ContractingClient,
)
from openprocurement_client.resources.lots import (
    LotsClient,
)
from openprocurement.caravan.constants import (
    config,
)


def get_contracting_client():
    return ContractingClient(
        key=config['contracting']['api']['token'],
        host_url=config['contracting']['api']['host'],
        api_version=config['contracting']['api']['version']
    )


def get_contracting_client_with_create_contract():
    return ContractingClient(
        key=config['contracting']['test']['token_with_create_contract_permission'],
        host_url=config['contracting']['api']['host'],
        api_version=config['contracting']['api']['version']
    )


def get_lots_client():
    return LotsClient(
        key=config['lots']['api']['token'],
        host_url=config['lots']['api']['host'],
        api_version=config['lots']['api']['version']
    )
