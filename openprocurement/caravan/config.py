# -*- coding: utf-8 -*-
import os

from munch import munchify

from openprocurement.caravan.utils import (
    load_file,
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TESTS_DIR = os.path.join(BASE_DIR, 'tests')
TEST_DATA_DIR = os.path.join(TESTS_DIR, 'data')


# logging.config.dictConfig(config_dict['logging'])
def app_config(config_filename=None):
    kv = {}

    if config_filename:
        file_data = load_file(config_filename)
        kv.update(file_data)

    return munchify(kv)
