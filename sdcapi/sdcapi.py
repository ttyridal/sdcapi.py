"""
sdcclient.py: SDC Mobile Banking API client

Copyright 2016, Torbjorn Tyridal

This program is relased under the GPLv3. See LICENSE for details.
"""
import base64
import copy
import datetime
import functools
import hashlib
import logging
import json
import os
import pprint
from posixpath import join as posix_join
import uuid
import ssl

import Crypto.Cipher.PKCS1_v1_5
import Crypto.Util
import Crypto.PublicKey.RSA
import certifi
import requests
import requests_toolbelt

from .sdccrypt import *

logger = logging.getLogger('sdcapi')

def _loadPublicKey(fname):
    with open(fname, 'r') as f:
        cert_bytes = f.read()
    cert_bytes = ssl.PEM_cert_to_DER_cert(cert_bytes)
    cert = Crypto.Util.asn1.DerSequence()
    cert.decode(cert_bytes)

    tbsCertificate = Crypto.Util.asn1.DerSequence()
    tbsCertificate.decode(cert[0])

    ## shaky, but seems to work on v1 and v3 certs.
    try:
        subjectPublicKeyInfo = tbsCertificate[6]
        serial = "%x"%tbsCertificate[1]
    except IndexError:
        serial = "%x"%tbsCertificate[0]
        subjectPublicKeyInfo = tbsCertificate[5]
    key = Crypto.PublicKey.RSA.importKey(subjectPublicKeyInfo)

    return type('Certificate', (object,), {'serial':serial.encode(), 'key':key})

def getRequestKey():
    # aeskey.. should probably be random :)
    return b'0'*16

def aesGetTransformation():
    return b'AES/CBC/PKCS5Padding'

def rsaGetTransformation():
    return b'RSA/ECB/PKCS1Padding'

def isAmountDict(d):
    return all((
        'currency' in d,
        'value' in d,
        'scale' in d,
        'localizedValueWithCurrency' in d,
        'roundedAmountWithCurrencySymbol' in d,
        'localizedValueWithCurrencyAtEnd' in d,
        'localizedValue' in d))

class Amount(object):
    def __init__(self, value, scale, currency):
        self.value = value
        self.scale = scale
        self.currency = currency
    def __repr__(self):
        return 'Amount({}, {}, {})'.format(self.value, self.scale, repr(self.currency))

class JSONWrap(object):
    def __init__(self, jsn, parent):
        self._json = jsn
        self._parent = parent
        self._dta = dict()

        for x in jsn:
            v = jsn[x]
            if isinstance(v, list):
                if all(isinstance(y, str) for y in v):
                    pass
                else:
                    v = [JSONWrap(y, parent) for y in v]
            elif isinstance(v, dict):
                if isAmountDict(v):
                    v = Amount(v['value'], v['scale'], v['currency'])
                else:
                    v = JSONWrap(v, parent)
            self._dta[x] = v

    def __repr__(self):
        return pprint.pformat(self._dta, indent=4)

    def __getattr__(self, name):
        return self._dta[name]

    def __delattr__(self, name):
        del self._dta[name]

class Agreement(JSONWrap):
    def select(self):
        return self._parent.select_agreement(self.entityKey)

class Account(JSONWrap):
    def transactions(self, dteStart=None, dteEnd=None, includeReservations=True):
        return self._parent.find_transactions(self.entityKey, dteStart, dteEnd, includeReservations)

class Transaction(JSONWrap):
    def details(self):
        return self._parent.transaction_details(self.entityKey)

class Reservation(JSONWrap): pass

class SDCapi(object):
    def __init__(self, bank_identifier, fake=False):
        self.urlbase = 'https://pilot.smartno.sdc.dk/restapi/'
        self.server_cert  = os.path.join(os.path.dirname(__file__),'sdc.pem')
        self.http = requests.Session()
        self.bankid = bank_identifier
        self.http.stream = True
        self.http.verify = certifi.where()  # '/etc/ssl/certs/ca-certificates.crt'
        self.http.headers = {
            'Accept-Encoding':'gzip',
            'Connection': 'Keep-Alive',
            'Accept': 'application/json, */*',
##             'User-Agent':'SDCClient Python/1.0.0',
            'User-Agent':'HockeySDK/Android',
            'X-SDC-LOCALE': 'nb_NO',
            'X-SDC-CLIENT-TYPE': 'smartphone',
            'Accept-Language': 'nb',
        }
        self.finalkey = None
        self.key = getRequestKey()

    def __enter__(self):
        return self

    def __exit__(self, eType, eValue, eTrace):
        self.close()
        return False

    def close(self):
        self.http.close()

    def url(self, path):
        return posix_join(self.urlbase, str(self.bankid), path)

    def _cryptoheaders(self, request_headers):
        if self.finalkey:
            return

        cert = _loadPublicKey(self.server_cert)
        base64Key = base64.b64encode(self.key)
        aestransform = b','.join([aesGetTransformation(), base64Key])
        sdccryptoinit = b','.join([cert.serial, rsaGetTransformation(), base64Encrypt(aestransform, Crypto.Cipher.PKCS1_v1_5, cert.key)])
        request_headers['X-SDC-CRYPTO-INIT'] = sdccryptoinit

    def _add_reqid(self, request_headers):
        reqid = base64Encrypt(b'id:'+str(uuid.uuid4()).encode(), AESPKCS5, self.key)
        request_headers['X-SDC-CRYPTO-REQUEST-ID'] = reqid

    def _cryptowrap(self, getpost, *args, **kwargs):
        kwargs['headers'] = kwargs.get('headers', dict())
        self._cryptoheaders(kwargs['headers'])

        self._add_reqid(kwargs['headers'])

        if 'json' in kwargs:
            kwargs['data'] = json.dumps(kwargs['json']).encode()
            kwargs['headers']['content-type'] = kwargs['headers'].get('content-type', 'application/json;charset=UTF-8')
            del kwargs['json']

        if 'data' in kwargs:
            kwargs['data'] = base64Encrypt(kwargs['data'], AESPKCS5, self.key)

        resp = getpost(*args, **kwargs)

        fk = resp.headers.get('X-SDC-FINAL-KEY')
        if fk:
            self.key = self.finalkey = base64Decrypt(fk, AESPKCS5, getRequestKey())
            logger.info("Got final key %s", self.finalkey)

        return resp

    def get(self, url, apiver, **kwargs):
        logger.info('============== GET %s ==================',url)
        kwargs['headers'] = kwargs.get('headers', dict())
        kwargs['headers']['X-SDC-API-VERSION'] = str(apiver)
        resp = self._cryptowrap(self.http.get, url, **kwargs)

        logger.debug("%s %s", resp.status_code, resp.reason)
        for k,v in resp.headers.items():
            logger.debug("%s: %s", k, v)


        if resp.content:
            try:
                resp._content = base64Decrypt(resp.content, AESPKCS5, self.finalkey)
            except: pass

        logger.debug(resp._content)

        resp.raise_for_status()

        return resp

    def post(self, url, apiver, **kwargs):
        logger.info('============== POST %s ==================', url)
        kwargs['headers'] = kwargs.get('headers', dict())
        kwargs['headers']['X-SDC-API-VERSION'] = str(apiver)

        if 'json' in kwargs:
            if 'logonpin' in url:
                kw = {}
                for k,v in kwargs['json'].items():
                    kw[k] = 'xxx'
            else:
                kw = kwargs['json']

            logger.debug(repr(kw))
        if 'data' in kwargs:
            logger.debug(repr(kwargs['data']))
        resp = self._cryptowrap(self.http.post, url, **kwargs)

        logger.debug("%s %s", resp.status_code, resp.reason)
        for k,v in resp.headers.items():
            logger.debug("%s: %s", k, v)

        if resp.content:
            try:
                resp._content = base64Decrypt(resp.content, AESPKCS5, self.finalkey)
            except: pass

        logger.debug(resp._content)

        resp.raise_for_status()

        return resp

    def launch(self):
        return self.post(self.url('launch/launch'), apiver=1, json={
            "appVersion":"4.0.0",
             "language":"en",
             "platform":"Android",
             "platformVersion":"6.0",
             "resolution":"480x800",
             "scale":"1"

            }).json()

    def site_info(self):
        return JSONWrap(self.get(self.url('miscellaneous/siteInformation'), apiver=1).json(), self)
        #, content_type='application/x-www-form-urlencoded')

    def login(self, userid, pin):
        resp = self.post(self.url('logon/logonpin'), apiver=3, json={
            'pin': pin,
            'userId': userid
        })
        try:
            d = json.loads(resp.text)
        except Exception as er:
            logger.exception("Exception %s\n data was:\n%s\n%s", str(er), resp, resp.text)
            raise
        return [ Agreement(x, self) for x in d ]

    def logout(self):
        return self.get(self.url('logon/logout'), 1).json()

    def select_agreement(self, agreementEntity):
        return JSONWrap(self.post(self.url('logon/selectagreement'), apiver=3, json=agreementEntity._json).json(), self)

    def overview(self):
        return self.get(self.url('miscellaneous/overview'), apiver=3).json()
        #, content_type='application/x-www-form-urlencoded')

    def accounts(self):
        accountPropertiesFilter = {
            'includeCreditAccounts': True,
            'includeDebitAccounts': True,
            'includeLoans': True,
            'onlyFavorites': False,
            'onlyQueryable': True,
        }
        d = self.post(self.url('accounts/list/filter'), apiver=1, json=accountPropertiesFilter).json()

        print("accounts:",d)


##         d = self.get(self.url('accounts/list/v1?clearCache=false')).json()
##         return [ Account(x, self) for x in d ]
        #, content_type='application/x-www-form-urlencoded')

    def efaktura_list(self):
        d = self.get(self.url('efaktura/list'), apiver=2).json()
        return [ JSONWrap(x, self) for x in d ]
        #, content_type='application/x-www-form-urlencoded')

    def bankingdays(self):
        return JSONWrap(self.get(self.url('miscellaneous/bankingdays'), apiver=1).json(), self)
        #, content_type='application/x-www-form-urlencoded')

    def find_transactions(self, accountEntity, dteFrom=None, dteTo=None, includeReservations=True):
        if dteTo is None:
            dteTo = datetime.date.today() if dteFrom is None else dteFrom.replace(day=1)
            dteTo = (dteTo.replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
        if dteFrom is None:
            dteFrom = datetime.date.today().replace(day=1)
        d = self.post(self.url('accounts/transactions/search'), apiver=5, json={
            "clearCache": True,
            "agreementId": accountEntity.agreementId,
            "accountId": accountEntity.accountId,
            "transactionsFrom": dteFrom.isoformat(),
            "transactionsTo": dteTo.isoformat(),
            "includeReservations":includeReservations
        }).json()

        transactions = [ Transaction(x, self) for x in d['transactions'] ]
        reservations = [ Reservation(x, self) for x in d['reservations'] ]
        return transactions + reservations


    def transaction_details(self, entityKey):
        return JSONWrap(self.post(self.url('accounts/transactions/details'), apiver=1, json=entityKey._json).json(), self)
