import csv
import hmac
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

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import RequestContext, loader
from django.utils import timezone

from . import models

APP_ID = 507982369367860
APP_SECRET = "213bdd72e269941abce42d09f8908765"
FACEBOOK_GRAPH_BASE_URI = 'https://graph.facebook.com/v2.5/'

'''
def import_csv(request):
    count = 0
    with open('C:\\Users\\user\\Projects\\social_age\\src\\sa\\socialage\\fb_twitter_lookup.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        try:
            while True:
                curr = next(reader)
                nt = next(reader)
                print(curr[0])
                while (curr[0] != nt[0]):
                    curr = nt
                    next = next(reader)
                if curr[3] == 'twitter':
                    tw_id = curr[2]
                    tw_handle = curr[4]
                    fb_id = nt[2]
                    fb_handle = nt[4]
                else:
                    fb_id = curr[2]
                    fb_handle = curr[4]
                    tw_id = nt[2]
                    tw_handle = nt[4]
                id = curr[0]
                name = curr[6]
                models.Page.objects.create(id=id,
                                           name=name,
                                           fb_id=fb_id,
                                           fb_handle=fb_handle,
                                           tw_id=tw_id,
                                           tw_handle=tw_handle,
                                           probs='0,0,0,0,0,0,0,0,0,0')
                count += 1
        except Exception as e:
            print str(e)
    return JsonResponse({'count': count})'''


def index(request):
    if not request.GET:  # New session - Facebook authentication
        request.session['index_uri'] = request.build_absolute_uri()
        return redirect(facebook_api_url_format('oauth/authorize', {'client_id': str(APP_ID),
                                                                    'redirect_uri': request.session.get('index_uri'),
                                                                    'scope': 'user_likes,user_birthday,user_friends'}))
    else:
        if request.GET.get('error_message'):
            return JsonResponse(request.GET)
        else:
            # Exchange code for access_token
            token = facebook_api_get('oauth/access_token',
                                     {'client_id': str(APP_ID),
                                      'redirect_uri': request.session.get('index_uri'),
                                      'client_secret': APP_SECRET,
                                      'code': request.GET.get("code")})
            request.session['access_token'] = token['access_token']
            # Get Facebook user id
            user = facebook_api_get('me', {'fields': 'id,name,birthday',
                                           'access_token': request.session.get('access_token')})
            request.session['user'] = user
        template = loader.get_template('results_ajax.html')
        context = RequestContext(request, {})
        return HttpResponse(template.render(context))


def results(request):
    user = request.session['user']
    try:
        facebook_user = models.FacebookUser.objects.get(id=user['id'])
        # Clear previous FacebookPageLike objects associated with the FacebookUser
        facebook_user.liked_pages.all().delete()
    except:
        facebook_user = None
    user_bday = timezone.make_aware(datetime.strptime(user['birthday'], '%m/%d/%Y'),
                                    timezone.UTC())
    if facebook_user is None:
        facebook_user = models.FacebookUser.objects.create(id=user['id'], name=user['name'],
                                                           birthday=user_bday)
    else:
        facebook_user.birthday = user_bday
        facebook_user.save()

    # Retrieve pages liked
    curr_page = facebook_api_get(user['id'] + '/likes/', {'access_token': request.session.get('access_token')})
    while curr_page.get('paging', False) and curr_page['paging'].get('next', False):
        next_page = curr_page['paging']['next']
        for p in curr_page['data']:
            try:
                page = models.Page.objects.get(fb_id=p['id'])
            except:
                page = None
            if page is None:
                page = models.Page.objects.create(id=uuid4(),
                                                  name=p['name'],
                                                  fb_id=p['id'],
                                                  fb_handle=p['name'],
                                                  probs='0,0,0,0,0,0,0,0,0,0')
            page_like_time = datetime.strptime(p['created_time'], '%Y-%m-%dT%H:%M:%S%z')
            page_like = models.FacebookPageLike.objects.create(user=facebook_user, page=page,
                                                               time=page_like_time)
        curr_page = http_get(next_page)
    liked_pages = {}
    try:
        facebook_user = models.FacebookUser.objects.get(id=request.session.get('user')['id'])
        liked_pages = facebook_user.liked_pages.all()
    except:
        pass
    template = loader.get_template('likes.html')
    context = RequestContext(request, {'username': facebook_user.name,
                                       'birthday': facebook_user.birthday.strftime('%d %B, %Y'),
                                       'pages_liked': liked_pages})
    return HttpResponse(template.render(context))


def facebook_api_url_format(url, params={}):
    return '{0}{1}?{2}'.format(FACEBOOK_GRAPH_BASE_URI, url, urllib.parse.urlencode(params))


def facebook_api_get(url, params={}):
    return http_get(facebook_api_url_format(url, params))


def http_get(url):
    request = urllib.request.urlopen(url)
    response = json.loads(request.read().decode("utf-8"))
    return response


def test(request):
    return JsonResponse({})


# ==========================================twitter API=============================================

CONSUMER_ID = "u49f8lp426j6EPQfvANuIWmIp"
CONSUMER_SECRET = "qDl3VJZ6KiIjiQxZN96QdopNRuLayIIPhdgqgkGdb4FMu4gffx"
BASE_API_URL = 'https://api.twitter.com/'


def twitter(request):
    if not request.GET:
        # Getting a request token
        hdr = {'oauth_callback': 'http://127.0.0.1:8080/twitter',
               'oauth_consumer_key': CONSUMER_ID,  # consumer id
               'oauth_nonce': oauth_nonce(),  # nonce
               'oauth_signature_method': 'HMAC-SHA1',  # signature method
               'oauth_timestamp': oauth_timestamp(),  # timestamp
               'oauth_version': '1.0'}
        signature = oauth_sign('POST', twitter_api_url_format('oauth/request_token'), hdr)
        hdr['oauth_signature'] = signature
        headers = twitter_header(hdr)
        token = twitter_api_post('oauth/request_token', headers)
        request.session['oauth_token'] = token['oauth_token']
        request.session['oauth_token_secret'] = token['oauth_token_secret']

        # Redirecting users to Twitter login page
        return redirect(twitter_api_url_format('oauth/authenticate', {'oauth_token': request.session['oauth_token']}))
    else:
        # Exchange request token for access token
        hdr = {'oauth_consumer_key': CONSUMER_ID,  # consumer id
               'oauth_nonce': oauth_nonce(),  # nonce
               'oauth_signature_method': 'HMAC-SHA1',  # signature method
               'oauth_timestamp': oauth_timestamp(),  # timestamp
               'oauth_token': request.session['oauth_token'],  # access token
               'oauth_version': '1.0'}
        signature = oauth_sign('POST', twitter_api_url_format('oauth/access_token'), hdr)
        hdr['oauth_signature'] = signature
        headers = twitter_header(hdr)
        token = twitter_api_post('oauth/access_token', headers, {'oauth_verifier': request.GET.get("oauth_verifier")})
        request.session['access_token'] = token['oauth_token']
        request.session['access_token_secret'] = token['oauth_token_secret']

        # Get twitter follower/ids
        follower_id_params = {'count': 5000, 'cursor': -1, 'screen_name': token['screen_name']}
        url = 'https://api.twitter.com/1.1/friends/ids.json?' + urllib.parse.urlencode(follower_id_params)
        hdr = {'oauth_consumer_key': CONSUMER_ID,  # consumer id
               'oauth_nonce': oauth_nonce(),  # nonce
               'oauth_signature_method': 'HMAC-SHA1',  # signature method
               'oauth_timestamp': oauth_timestamp(),  # timestamp
               'oauth_token': request.session['access_token'],  # access token
               'oauth_version': '1.0'}
        follower_id_params.update(hdr)
        signature = oauth_sign('GET',
                               twitter_api_url_format('1.1/friends/ids.json'),
                               follower_id_params,
                               request.session['access_token_secret'])
        hdr['oauth_signature'] = signature
        headers = ('OAuth ' + ', '.join(list(map(lambda x: str(x[0]) + '="' + str(x[1]) + '"', sorted(hdr.items())))))
        follower_id_request = urllib.request.Request(url)
        follower_id_request.add_header('Authorization', headers)
        ids = json.loads(urllib.request.urlopen(follower_id_request).read().decode('utf-8'))
        return JsonResponse(ids)


'''
Takes a dictionary of key values required by the Twitter API and
returns the header. Add the header to the HTTP request by

   request.add_header('Authorization', headers)
'''


def twitter_header(dict):
    return ('OAuth ' + ', '.join(list(map(lambda x: str(x[0]) + '="' + str(x[1]) + '"', sorted(dict.items())))))


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
        return (BASE_API_URL + url)
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
