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
from django.views.decorators.csrf import csrf_exempt

from . import models

APP_ID = 507982369367860
APP_SECRET = "213bdd72e269941abce42d09f8908765"
FACEBOOK_GRAPH_BASE_URI = 'https://graph.facebook.com/v2.5/'


def index(request):
    template = loader.get_template('index.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))


def facebook(request):
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
        #return redirect('fb_results')
        print({"user_id": request.session['user']['id'], "token": request.session['access_token']})
        return HttpResponse(template.render(context))

'''
Facebook API to get liked pages.

POST request to /fb_api/ with access_token.

Returns JSON containing a status value indicating
error or success, an error_msg if and error has occured,
the facebook user's name, birthday and id, and the list of
liked pages.
'''
@csrf_exempt
def fb_api(request):
    access_token = request.POST.get('access_token', -1)
    if access_token == -1:
        return JsonResponse({"status": "error", "error_msg": "Missing access_token."})
    fb_user = facebook_api_get('me', {'fields': 'id,name,birthday',
                                           'access_token': access_token})
    try:
        user_id = request.session.get('user_id', None)
        if user_id:
            user = models.User.objects.get(id=user_id)
        else:
            user = models.User.objects.get(fb_id=fb_user['id'])
        # Clear previous FacebookPageLike objects associated with the User
        user.liked_pages.all().delete()
    except:
        user = None
    try:
        user_bday = timezone.make_aware(datetime.strptime(fb_user['birthday'], '%m/%d/%Y'),
                                    timezone.UTC())
        if user is None:
            user = models.User.objects.create(fb_id=fb_user['id'], name=fb_user['name'],
                                          birthday=user_bday)
        else:
            user.birthday = user_bday
            user.save()
    except:
        if user is None:
            user = models.User.objects.create(fb_id=fb_user['id'], name=fb_user['name'])

    request.session['user_id'] = user.id

    # Retrieve pages liked
    curr_page = facebook_api_get(fb_user['id'] + '/likes/', {'access_token': access_token})
    pages = []
    while curr_page.get('paging', False) and curr_page['paging'].get('next', False):
        next_page = curr_page['paging']['next']
        for p in curr_page['data']:
            try:
                page = models.Page.objects.get(fb_id=p['id'])
            except:
                page = None
            if page is None:
                page = models.Page.objects.create(name=p['name'],
                                                  fb_id=p['id'],
                                                  fb_handle=p['name'])
            page_like_time = datetime.strptime(p['created_time'], '%Y-%m-%dT%H:%M:%S%z')
            page_like = models.FacebookPageLike.objects.create(user=user, page=page,
                                                               time=page_like_time)
            pages.append({'id': p['id'], 'name': p['name'], 'time_liked': page_like_time})
        curr_page = http_get(next_page)
    return JsonResponse({"status": "success", "user": fb_user, "liked_pages": pages})


def fb_results(request):
    fb_user = request.session['user']
    try:
        user_id = request.session.get('user_id', None)
        if user_id:
            user = models.User.objects.get(id=user_id)
        else:
            user = models.User.objects.get(fb_id=user['id'])
        # Clear previous FacebookPageLike objects associated with the User
        user.liked_pages.all().delete()
    except:
        user = None
    user_bday = timezone.make_aware(datetime.strptime(fb_user['birthday'], '%m/%d/%Y'),
                                    timezone.UTC())
    if user is None:
        user = models.User.objects.create(fb_id=fb_user['id'], name=fb_user['name'],
                                          birthday=user_bday)
    else:
        user.birthday = user_bday
        user.save()
    request.session['user_id'] = user.id
    # Retrieve pages liked
    curr_page = facebook_api_get(fb_user['id'] + '/likes/', {'access_token': request.session.get('access_token')})
    while curr_page.get('paging', False) and curr_page['paging'].get('next', False):
        next_page = curr_page['paging']['next']
        for p in curr_page['data']:
            try:
                page = models.Page.objects.get(fb_id=p['id'])
            except:
                page = None
            if page is None:
                page = models.Page.objects.create(name=p['name'],
                                                  fb_id=p['id'],
                                                  fb_handle=p['name'])
            page_like_time = datetime.strptime(p['created_time'], '%Y-%m-%dT%H:%M:%S%z')
            page_like = models.FacebookPageLike.objects.create(user=user, page=page,
                                                               time=page_like_time)
        curr_page = http_get(next_page)
    return redirect('results')

def results(request):
    user = models.User.objects.get(id=request.session['user_id'])

    ## TODO : PUT THE LIKEDPAGES INTO THE MODEL ##

    template = loader.get_template('likes.html')
    context = RequestContext(request, {'username': user.name,
                                       'birthday': user.birthday.strftime('%d %B, %Y'),
                                       'pages_liked': user.liked_pages.all(),
                                       'followed': user.followed_pages.all(),
                                       'has_fb': -1 if len(user.liked_pages.all()) == 0 else 0,
                                       'has_tw': -1 if len(user.followed_pages.all()) == 0 else 0})

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
        hdr = {'oauth_callback': 'http://localhost:8080/twitter',
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
        request.session['tw_id'] = token['user_id']
        request.session['tw_screen_name'] = token['screen_name']
        template = loader.get_template('results_ajax_tw.html')
        context = RequestContext(request, {})
        # return redirect('twitter_results')
        return HttpResponse(template.render(context))


def twitter_results(request):
    try:
        user_id = request.session.get('user_id', None)
        if user_id:
            user = models.User.objects.get(id=user_id)
        else:
            user = models.User.objects.get(tw_id=request.session['tw_id'])
        # Clear previous FacebookPageLike objects associated with the User
        user.followed_pages.all().delete()
    except:
        user = models.User.objects.create(tw_id=request.session['tw_id'], name=request.session['tw_screen_name'])

    request.session['user_id'] = user.id

    # Get twitter follower/ids
    cursor = -1
    while cursor != 0:
        friends_params = {'count': 5000, 'cursor': cursor, 'screen_name': request.session['tw_screen_name']}
        url = 'https://api.twitter.com/1.1/friends/list.json?' + urllib.parse.urlencode(friends_params)
        hdr = {'oauth_consumer_key': CONSUMER_ID,  # consumer id
               'oauth_nonce': oauth_nonce(),  # nonce
               'oauth_signature_method': 'HMAC-SHA1',  # signature method
               'oauth_timestamp': oauth_timestamp(),  # timestamp
               'oauth_token': request.session['access_token'],  # access token
               'oauth_version': '1.0'}
        friends_params.update(hdr)
        signature = oauth_sign('GET',
                               twitter_api_url_format('1.1/friends/list.json'),
                               friends_params,
                               request.session['access_token_secret'])
        hdr['oauth_signature'] = signature
        headers = (
            'OAuth ' + ', '.join(list(map(lambda x: str(x[0]) + '="' + str(x[1]) + '"', sorted(hdr.items())))))
        friends_request = urllib.request.Request(url)
        friends_request.add_header('Authorization', headers)
        friends = json.loads(urllib.request.urlopen(friends_request).read().decode('utf-8'))
        cursor = friends['next_cursor']
        for f in friends['users']:
            try:
                page = models.Page.objects.get(tw_id=f['id'])
            except:
                page = models.Page.objects.create(name=f['name'],
                                                  tw_id=f['id'],
                                                  tw_handle=f['screen_name'])
            follow = models.TwitterFollow.objects.create(user=user, page=page)

    return redirect('results')


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
