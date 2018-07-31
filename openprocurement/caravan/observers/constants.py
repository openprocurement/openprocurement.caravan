# -*- coding: utf-8 -*-

# Ceasefire
CONTRACT_STATUS_MAPPING = {
    "pending.terminated": "complete",
    "pending.unsuccessful": "unsuccessful",
}
LOT_CONTRACT_TERMINAL_STATUSES = [CONTRACT_STATUS_MAPPING[key] for key in CONTRACT_STATUS_MAPPING.keys()]
PRE_TERMINATED_STATUS_PREFIX = 'pending.'
