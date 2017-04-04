#!/usr/bin/env python3
"""
example.py

demonstration of sdcapi.py
"""
from __future__ import print_function

import datetime
import logging
from netrc import netrc
import pprint
import sys
import warnings

import requests

from sdcapi.sdcapi import SDCapi, Transaction

warnings.simplefilter('error')
warnings.simplefilter('ignore', requests.packages.urllib3.exceptions.InsecureRequestWarning)


def configure_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='client.log',
                        filemode='w')
    logging.getLogger('requests').setLevel(logging.ERROR)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
    logging.getLogger('').addHandler(console)



def select_one(lst, prop):
    while 1:
        for i, ag in enumerate(lst, 1):
            print("{}: {}".format(i, prop(ag)))
        try:
            return lst[int(input('>'))-1]
        except Exception as e:
            print(e)
            continue
        except KeyboardInterrupt:
            return None

def main():
    configure_logging()
    print("see bankidentifiers.pdf for your bank id")
    bankid = int(input("Enter your bank id >"))

    with SDCapi(bank_identifier=bankid) as api:
        username, _, pin = netrc().authenticators('sdcbank')
        agreements = api.login(username, pin)

        if len(agreements) > 1:
            ag = select_one(agreements, lambda x: x.agreementName)
            ag.select()
        else:
            agreements[0].select()

        print("\n".join(repr(x) for x in api.efaktura_list()))

        print("Select account for transaction list")
        accounts = api.accounts()
        ag = select_one(accounts, lambda x: x.name)

        for t in ag.transactions(datetime.date(2016,1,1),datetime.date(2016,3,1) - datetime.timedelta(days=1)):
            print("{}({}),".format(t.__class__.__name__, pprint.pformat(t._dta, indent=4)))


if __name__ == '__main__':
    sys.exit(main())
