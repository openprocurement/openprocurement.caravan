# -*- coding: utf-8 -*-
import logging


_log_conf_dict = {
    'version': '1'
}

logging.basicConfig()
LOGGER = logging.getLogger('caravan')
LOGGER.setLevel(logging.INFO)
