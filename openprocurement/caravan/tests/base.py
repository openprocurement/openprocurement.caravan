# -*- coding: utf-8 -*-
import os

from unittest import TestCase
from openprocurement.caravan.config import (
    app_config,
    TESTS_DIR,
)
from openprocurement.caravan.utils import (
    connect_to_db_server,
    db_url,
    get_db,
)
from openprocurement_client.resources.contracts import (
    ContractingClient,
)
from openprocurement_client.resources.lots import (
    LotsClient,
)


class CeasefireLokiBaseTest(TestCase):

    def setUp(self):
        self.config = app_config(os.path.join(TESTS_DIR, 'test_config.yaml'))
        db_config = self.config.contracting.db
        url_db = db_url(db_config.protocol, db_config.host, db_config.port)
        self.db_server = connect_to_db_server(url_db, db_config.retries_on_connect)

        self.db = get_db(db_config.name, self.db_server)

        self.dockey = self.config.test.dockey

        contracting_api = self.config.contracting.api

        self.contracting_client_with_create = ContractingClient(
            host_url=contracting_api.host,
            api_version=contracting_api.version,
            key=self.config.contracting.test.token_with_create_contract_permission
        )

        self.contracting_client = ContractingClient(
            host_url=contracting_api.host,
            api_version=contracting_api.version,
            key=contracting_api.token,
        )

        lots_api = self.config.lots.api

        self.lots_client = LotsClient(
            host_url=lots_api.host,
            api_version=lots_api.version,
            key=lots_api.token
        )
