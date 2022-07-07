#!/usr/bin/env python3
# coding=utf8
"""
example.py

demonstration of sdcapi.py
"""
import argparse
import datetime
import logging
from netrc import netrc
import pprint
from pathlib import Path
import sys
import warnings
import json

import requests

from sdcapi.sdcapi import SDCapi, Transaction

warnings.simplefilter('error')
warnings.simplefilter('ignore', requests.packages.urllib3.exceptions.InsecureRequestWarning)


def configure_logging(verbose):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='client.log',
                        filemode='w')
    logging.getLogger('requests').setLevel(logging.ERROR)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO if verbose < 1 else logging.DEBUG)
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


def getconfig(verbose):
    p = Path('config.json')
    config = {'verbose': verbose}
    if p.exists():
        with open(p) as f:
            config.update(json.load(f))

    if not all((config.get('username', None), config.get('userpin', None))):
        username, _, pin = netrc().authenticators('sdcbank')
        config['username'] = username
        config['userpin'] = pin

    return config


def main():
    parser = argparse.ArgumentParser(description='sdcapi example')
    parser.add_argument('-v', '--verbose', action='count', default=0,  help='''verbose''')
    args = parser.parse_args()

    config = getconfig(args.verbose)
    configure_logging(config['verbose'])

    if not config.get('bank_identifier', None):
        print("see bankidentifiers.pdf for your bank id")
        config['bank_identifier'] = int(input("Enter your bank id >"))

    with SDCapi(bank_identifier=config['bank_identifier']) as api:
        #print(api.bankingdays())
        #return

        agreements = api.login(config['username'], config['userpin'])
        api.http.headers['X-SDC-DEVICE-TOKEN'] = api.getDeviceToken(api.getChallenge())

        if len(agreements) > 1:
            ag = select_one(agreements, lambda x: x.agreementName)
            ag.select()
        else:
            agreements[0].select()

        print("\n".join(repr(x) for x in api.efaktura_list()))

        print("Select account for transaction list")
        accounts = api.accounts()
        ag = select_one(accounts, lambda x: x.name)

        for t in ag.transactions(datetime.date(2022,1,1),datetime.date(2022,3,1) - datetime.timedelta(days=1)):
            print("{}({}),".format(t.__class__.__name__, pprint.pformat(t._dta, indent=4)))


if __name__ == '__main__':
    sys.exit(main())
