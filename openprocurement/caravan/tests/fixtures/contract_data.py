# -*- coding: utf-8 -*-
from datetime import datetime, timedelta


now = datetime.now()
now_iso = now.isoformat()
tomorrow = now + timedelta(days=1)
tomorrow_iso = tomorrow.isoformat()

contract_create_data = {
    "data": {
        "merchandisingObject": "a930574bf8cd999cb7f9c9ed4ca68061",
        "relatedProcessID": "0b7bca6feeb644e987ded0429f1ec167",
        "procuringEntity": {
            "contactPoint": {
                "name": "Україна",
                "telephone": "0440000000"
            },
            "identifier": {
                "scheme": "UA-EDR",
                "id": "00037256",
                "uri": "http://www.dus.gov.ua/"
            },
            "name": "Buy a Garage",
            "address": {
                "countryName": "Ukraine",
                "postalCode": "01220",
                "region": "Lviv",
                "streetAddress": "Ololo st. 69",
                "locality": "Psykhiv"
            }
        },
        "title": "Test Contract",
        "suppliers": [{
            "contactPoint": {
                "name": "Andreas",
                "telephone": "0440000000"
            },
            "identifier": {
              "scheme": "UA-EDR",
              "id": "00037256",
              "uri": "http://www.dus.gov.ua/"
            },
            "name": "blabla corp.",
            "address": {
                 "countryName": "Ukraine",
                 "postalCode": "01220",
                 "region": "Lviv",
                 "streetAddress": "Ololo",
                 "locality": "Psykhiv"
            }
        }],
        "contractType": "ceasefire",
        "awardID": "376d560b2b2d452a80543865f3cab43e",
        "period": {
            "startDate": now_iso,
            "endDate": tomorrow_iso
        },
        "dateSigned": now_iso,
        "contractID": "a930574bf8cd405cb7f9c9ed4ca68061"
    }
}
