# -*- coding: utf-8 -*-
import signal
from openprocurement.caravan.log import LOGGER


class GracefulKiller(object):
    kill = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        LOGGER.info("Gracefully stop")
        self.kill = True
