# -*- coding: utf-8 -*-
import json
import yaml
import logging
import socket
import argparse

from couchdb import Server, Session
from uuid import uuid4

from logging import getLogger

LOGGER = getLogger('openprocurement.caravan')


def db_url(protocol, host, port):
    return "{0}://{1}:{2}".format(protocol, host, port)


def connect_to_db_server(url, retries, check_connection=True):
    """Connect to the CouchDB

    :param retries: list like [1, 2, 3]
    """
    server = Server(url, session=Session(retry_delays=retries))
    if check_connection:
        db_name = ''.join(('test_', uuid4().hex))
        try:
            server.create(db_name)
        except socket.error as exc:
            logging.error(
                "Cannot use DB due to socket error (maybe DB isn't working): {0}".format(exc.message)
            )
            return None
        except Exception:
            logging.error("Cannot use DB due to some error")
            return None
        else:
            server.delete(db_name)
    return server


def get_db(name, server):
    """Get or create database"""
    try:
        if name not in server:
            db = server.create(name)
        else:
            db = server[name]
    except Exception:
        return None
    return db


def load_fixture(filepath, db):
    """Load some documents into DB from file

    File will be searched in TEST_DATA_DIR.
    Data should be like:
        [{doc1}, {doc2}, ... {docN}]
    """
    with open(filepath, 'r') as f:
        file_content = f.read()
    data = json.loads(file_content)
    for doc in data:
        db.save(doc)


def search_list_with_dicts(container, key, value):
    """Search for dict in list with dicts

    Useful for searching for milestone in the list of them.

    :param container: an iterable to search in
    :param key: key of dict to check
    :param value: value of key to search

    :returns: first acceptable dict
    """
    for item in container:
        found_value = item.get(key, False)
        if found_value and found_value == value:
            return item


def providedBy_or_error(interface, obj):
    if not interface.providedBy(obj):
        raise TypeError(
            "Object must implement interface {0}".format(
                interface.__name__
            )
        )


def clean_db(db):
    for doc in db:
        del db[doc]


def search_lot_contract_by_related_contract(lot_client, lot_id, related_contract_id):
    """Returns munch with contract data, if found. Otherwise - returns None"""
    lot = lot_client.get_lot(lot_id)
    contract = search_list_with_dicts(lot.data.contracts, 'relatedProcessID', related_contract_id)
    return contract


def parse_args():
    parser = argparse.ArgumentParser(
        description='Synchronize Ceasefire contracting with Loki lots'
    )
    parser.add_argument('config', type=str, help='Path to configuration file')
    params = parser.parse_args()
    return params


def load_file(path):
    file_extension = path.split('.')[-1]

    readers = {  # let's make file format less important
        'yaml': yaml.safe_load,
        'yml': yaml.safe_load,
        'json': json.loads,
    }

    reader_method = readers.get(file_extension)

    with open(path, 'r') as f:
        data = f.read()

    parsed_file = reader_method(data)
    return parsed_file
