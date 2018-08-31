# -*- coding: utf-8 -*-
import logging
import logging.config


_format = '%(levelname)s: %(message)s'
# other attributes of log record are described here:
# https://docs.python.org/2/library/logging.html#logrecord-attributes

logging.basicConfig(format=_format)
LOGGER = logging.getLogger('caravan')
LOGGER.setLevel(logging.INFO)
