# -*- coding: utf-8 -*-
import os
import yaml


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TESTS_DIR = os.path.join(BASE_DIR, 'tests')
TEST_DATA_DIR = os.path.join(TESTS_DIR, 'data')

# Relation btw contract model in contracting and lots
CONTRACT_STATUS_MAPPING = {
    "pending.terminated": "complete",
    "pending.unsuccessful": "unsuccessful",
}
PRE_TERMINATED_STATUS_PREFIX = 'pending.'

CONFIG_NAME = 'config.yaml'
CONFIG_PATH = os.path.join(BASE_DIR, CONFIG_NAME)

with open(CONFIG_PATH) as config_file:
    config = yaml.safe_load(config_file.read())
