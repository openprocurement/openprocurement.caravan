# -*- coding: utf-8 -*-
import unittest
from socket import error
from mock import (
    MagicMock,
    Mock,
    patch,
)
from openprocurement.caravan.utils import (
    connect_to_db_server,
    get_db,
)


class ConnectToDBTest(unittest.TestCase):

    @patch('openprocurement.caravan.utils.Session')
    @patch('openprocurement.caravan.utils.Server')
    def test_ok(self, server, session):
        url = 'http://localhost:5984'
        server.return_value = 'ok'
        server = connect_to_db_server(url, [1, 2], check_connection=False)
        assert server == 'ok'

    @patch('openprocurement.caravan.utils.Session')
    @patch('openprocurement.caravan.utils.Server')
    def test_no_connection(self, server, session):
        url = 'http://localhost:100500'
        create_db_mock = Mock()
        create_db_mock.create.side_effect = error
        server.return_value = create_db_mock
        created_server = connect_to_db_server(url, (1, 2))
        assert created_server is None


class GetDBTest(unittest.TestCase):

    def test_ok_but_must_create_db(self):
        server = MagicMock()
        server.__contains__.return_value = []
        server_response_created = 'ok-created'
        server.create.return_value = server_response_created
        name = 'mock_name'
        result = get_db(name, server)
        assert result == server_response_created

    def test_ok_db_was_already_created(self):
        name = 'mock_name'

        server = MagicMock()
        server.__contains__.return_value = [name]
        server.__getitem__.return_value = 'ok'
        result = get_db(name, server)
        assert result == 'ok'
