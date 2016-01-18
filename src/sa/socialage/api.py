import csv
import hmac
import math
import time
import random
import string
import hashlib
from base64 import b64encode
from uuid import uuid4

from datetime import datetime
import json
import urllib.request
import urllib.parse

APP_ID = 507982369367860
APP_SECRET = "213bdd72e269941abce42d09f8908765"
FACEBOOK_GRAPH_BASE_URI = 'https://graph.facebook.com/v2.5/'

CONSUMER_ID = "u49f8lp426j6EPQfvANuIWmIp"
CONSUMER_SECRET = "qDl3VJZ6KiIjiQxZN96QdopNRuLayIIPhdgqgkGdb4FMu4gffx"
BASE_API_URL = 'https://api.twitter.com/'

'''
Takes a dictionary of key values required by the Twitter API and
returns the header. Add the header to the HTTP request by

   request.add_header('Authorization', headers)
'''


def twitter_header(dict):
    return 'OAuth ' + ', '.join(list(map(lambda x: str(x[0]) + '="' + str(x[1]) + '"', sorted(dict.items()))))


def oauth_sign(method, url, dict, oauth_token_secret=''):
    base_string = '&'.join(list(map(lambda x: str(x[0]) + '=' + str(x[1]), sorted(dict.items()))))
    signing_key = CONSUMER_SECRET + '&' + oauth_token_secret
    base_string = '{0}&{1}&{2}'.format(method, urllib.parse.quote(url, safe=''),
                                       urllib.parse.quote(base_string, safe=''))
    hash = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1)
    sign = b64encode(hash.digest())
    return urllib.parse.quote(sign.decode())


def oauth_nonce():
    random_string = ''.join(list((random.choice(string.ascii_letters + string.digits)) for i in range(32)))
    return random_string


def oauth_timestamp():
    return str(int(time.time()))


# Construct http requests
def twitter_api_url_format(url, params={}):
    if params == {}:
        return BASE_API_URL + url
    else:
        return '{0}{1}?{2}'.format(BASE_API_URL, url, urllib.parse.urlencode(params))


def twitter_api_post(url, headers, data={}):
    url = twitter_api_url_format(url)
    req = urllib.request.Request(url)
    req.add_header('Authorization', headers)
    enc_data = urllib.parse.urlencode(data)
    content_length = len(enc_data)
    if content_length > 0:
        req.add_header('Content-Length', content_length)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    request = urllib.request.urlopen(req, enc_data.encode())
    rep1 = request.read().decode('utf-8').split('&')
    rep2 = {}
    for i in rep1:
        kv = i.split('=')
        rep2[kv[0]] = kv[1]
    return rep2


def facebook_api_url_format(url, params={}):
    return '{0}{1}?{2}'.format(FACEBOOK_GRAPH_BASE_URI, url, urllib.parse.urlencode(params))


def facebook_api_get(url, params={}):
    return http_get(facebook_api_url_format(url, params))


def http_get(url):
    request = urllib.request.urlopen(url)
    response = json.loads(request.read().decode("utf-8"))
    return response
