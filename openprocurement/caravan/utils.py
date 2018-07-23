# -*- coding: utf-8 -*-
import json
import logging
import os
import random
import socket

from couchdb import Server, Session
from pkg_resources import get_distribution
from uuid import uuid4

from logging import getLogger
from openprocurement.caravan.constants import (
    config,
    TEST_DATA_DIR,
)

LOGGER = getLogger('openprocurement.caravan')


def connect_to_db_server(url, check_connection=True):
    """Connect to the CouchDB"""
    server = Server(url, session=Session(retry_delays=config['contracting']['db']['retries_on_connect']))
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


def prepare_db():
    """Shorthand helper to prepare DB in one call"""
    server = connect_to_db_server(config['contracting']['db']['url'])
    db = get_db(config['contracting']['db']['name'], server)
    return server, db


def load_file(filename):
    with open(filename) as f:
        return f.read()


def load_fixture(filename, db):
    """Load some documents into DB from file

    File will be searched in TEST_DATA_DIR.
    Data should be like:
        [{doc1}, {doc2}, ... {docN}]
    """
    fixture_path = os.path.join(TEST_DATA_DIR, filename)
    file_content = load_file(fixture_path)
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


def get_sleep_time():
    min_sleep_time = config['runner']['sleep_seconds']['min']
    max_sleep_time = config['runner']['sleep_seconds']['max']
    return random.randint(min_sleep_time, max_sleep_time)


def clean_db(db):
    for doc in db:
        del db[doc]


def search_lot_contract_by_related_contract(lot_client, lot_id, related_contract_id):
    """Returns munch with contract data, if found. Otherwise - returns None"""
    lot = lot_client.get_lot(lot_id)
    contract = search_list_with_dicts(lot.data.contracts, 'relatedProcessID', related_contract_id)
    return contract
