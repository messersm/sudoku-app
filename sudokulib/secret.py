# -*- coding: utf-8 -*-

from hashlib import sha1


def get_secret(s):
    key = sha1(s).hexdigest()
    return SECRETS.get(key, None)

SECRETS = {
    "fa56b440b285c9255b136cc4242f14bc8c795147": "" +
    "300000401" +
    "100000000" +
    "000001987" +
    "030004010" +
    "010000000" +
    "000019870" +
    "003040100" +
    "001000000" +
    "000198700"
}
