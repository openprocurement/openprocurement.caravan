# -*- coding: utf-8 -*-
import os
import logging.config

from munch import munchify

from openprocurement.caravan.utils import (
    load_file,
    LOGGER,
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TESTS_DIR = os.path.join(BASE_DIR, 'tests')
TEST_DATA_DIR = os.path.join(TESTS_DIR, 'data')


def try_config_logging_from_dict(config_dict):
    """Search for `logging` section in a dict and try to use it as logging config"""
    if config_dict.get('logging'):
        logging.config.dictConfig(config_dict['logging'])
        LOGGER.info('Use logging settings from the config file')
    LOGGER.info('Tried to use logging settings from the config file, but have not foud `logging` section')


def app_config(config_filename=None):
    kv = {}

    if config_filename:
        file_data = load_file(config_filename)
        try_config_logging_from_dict(file_data)
        kv.update(file_data)

    return munchify(kv)
