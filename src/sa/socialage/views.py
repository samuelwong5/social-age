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
from datetime import date, timedelta
import json
import urllib.request
import urllib.parse

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import RequestContext, loader
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum

from . import age_table
from . import models
from . import predict
from .api import *

APP_ID = 507982369367860
APP_SECRET = "213bdd72e269941abce42d09f8908765"
FACEBOOK_GRAPH_BASE_URI = 'https://graph.facebook.com/v2.5/'


def index(request):
    template = loader.get_template('index_test.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))


# =====================================================================================================
# ============================================ APIs  ==================================================
# =====================================================================================================


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
            print(request.session['access_token'])
            # Get Facebook user id
            user = facebook_api_get('me', {'fields': 'id,name,birthday',
                                           'access_token': request.session.get('access_token')})
            request.session['user'] = user
            profile_pic = "http://graph.facebook.com/" + user['id'] + "/picture?height=170&width=170"
        template = loader.get_template('result_loading.html')
        context = RequestContext(request, {'api': 'fb',
                                           'profile_pic': profile_pic})
        # return redirect('fb_results')
        return HttpResponse(template.render(context))


def fb_results(request):
    fb_user = request.session['user']
    user_bday = timezone.make_aware(datetime.strptime(fb_user['birthday'], '%m/%d/%Y'), timezone.UTC())
    try:
        user_id = request.session.get('user_id', None)
        if user_id:
            user = models.User.objects.get(id=user_id)
            user.name = fb_user['name']
            user.fb_id = fb_user['id']
        else:
            user = models.User.objects.get(fb_id=user['id'])
        user.birthday = user_bday
        user.save()
        # Clear previous FacebookPageLike objects associated with the User
        user.liked_pages.all().delete()
    except:
        user = models.User.objects.create(fb_id=fb_user['id'], name=fb_user['name'], birthday=user_bday)
    request.session['user_id'] = user.id
    # Retrieve pages liked
    curr_page = facebook_api_get(fb_user['id'] + '/likes/', {'access_token': request.session.get('access_token')})
    while curr_page.get('paging', False) and curr_page['paging'].get('next', False):
        next_page = curr_page['paging']['next']
        for p in curr_page['data']:
            try:
                page = models.Page.objects.get(fb_id=p['id'])
                page_like_time = datetime.strptime(p['created_time'], '%Y-%m-%dT%H:%M:%S%z')
                page_like = models.FacebookPageLike.objects.create(user=user, page=page, time=page_like_time)
            except:
                try:
                    page = models.Page.objects.create(name=p['name'],
                                                      fb_id=p['id'],
                                                      fb_handle=p['id'])
                    page_like_time = datetime.strptime(p['created_time'], '%Y-%m-%dT%H:%M:%S%z')
                    page_like = models.FacebookPageLike.objects.create(user=user, page=page,
                                                                       time=page_like_time)
                except:
                    pass
        curr_page = http_get(next_page)

    # Retrieve friends
    friends = facebook_api_get('me/friends', {'access_token': request.session.get('access_token')})
    friend_ids = list(map(lambda x: x['id'], friends['data']))
    user.fb_friends = ','.join(friend_ids)
    user.save()

    return redirect('results')


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
        profile_pic = "https://twitter.com/" + token['screen_name'] + "/profile_image?size=original"
        template = loader.get_template('result_loading.html')
        context = RequestContext(request, {'api': 'tw',
                                           'profile_pic': profile_pic})
        # return redirect('twitter_results')
        return HttpResponse(template.render(context))


def twitter_results(request):
    try:
        user_id = request.session.get('user_id', None)
        if user_id:
            user = models.User.objects.get(id=user_id)
            user.tw_id = request.session['tw_id']
            user.tw_handle = request.session['tw_screen_name']
            user.save()
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
            pages.append({'id': p['id'], 'name': p['name'], 'time_liked': page_like_time, 'average_age': page.prob()})
        curr_page = http_get(next_page)

    age = predict.predict(list(map(lambda x: x.page.fb_id, user.liked_pages.all())), 'fb')
    return JsonResponse({"status": "success", "user": fb_user, "liked_pages": pages, "social_age": round(age)})


# =====================================================================================================
# ===================================== Result pages ==================================================
# =====================================================================================================

"""
These are called with AJAX to replace content of result_page.html
"""


def results(request):
    user_id = request.GET.get('id', 0)
    if user_id == 0:
        user_id = request.session['user_id']
    user = models.User.objects.get(id=user_id)
    if user is None:
        return redirect('index')
    fb_page_ids = list(map(lambda x: x.page.fb_id, user.liked_pages.all()))
    tw_page_ids = list(map(lambda x: x.page.tw_id, user.followed_pages.all()))
    age = predict.predict(fb_page_ids, tw_page_ids)
    age = round(age)
    bio_age = int((date.today() - user.birthday.date()).days / 365.2425)
    if user.age < 0:  # First time, dont decrement age table
        user.age = bio_age
    else:  # Decrement previous age table entry
        age_table.age_table_sub(bio_age, user.social_age)
        user.social_age = age
    age_table.age_table_add(bio_age, age)
    user.save()
    msg = gen_message(bio_age, age)
    # if url contains resultpage, load template with nav bar and header as well, instead of
    # just the content.
    if "resultpage" in request.build_absolute_uri():
        template = loader.get_template('result_page.html')
    else:
        template = loader.get_template('result_content.html')
    dict = {'username': user.name,
            'birthday': user.birthday.strftime('%d %B, %Y'),
            'age': bio_age,
            'social_age': age,
            'user_id': user_id,
            'message': msg}
    if "resultpage" in request.build_absolute_uri():
        if user.fb_id == -1:
            dict['profile_pic'] = "https://twitter.com/" + user.tw_id + "/profile_image?size=original"
        else:
            dict['profile_pic'] = "http://graph.facebook.com/" + user.fb_id + "/picture?height=170&width=170"
        dict['has_fb'] = 0 if user.fb_id == "-1" else 1
        dict['has_tw'] = 0 if user.tw_id == "-1" else 1
    context = RequestContext(request, dict)
    return HttpResponse(template.render(context))


def recommended(request):
    user_id = request.GET.get('id', 0)
    if user_id == 0:
        user_id = request.session['user_id']
    user = models.User.objects.get(id=user_id)
    if user is None:
        return redirect('index')
    # Generate a list of 10 of recommended pages for the users, excluding liked or followed ones,
    # Also generate the links to the pages and profile picture of the pages.
    fb_page_ids = fb_pages_from_user(user)
    tw_page_ids = tw_pages_from_user(user)
    rpages_a = predict.recommend(age_from_birthday(user.birthday), exclude_fbids=fb_page_ids,
                                 exclude_twids=tw_page_ids, page_needed=10)
    rpages_s = predict.recommend(user.social_age, exclude_fbids=fb_page_ids,
                                 exclude_twids=tw_page_ids, page_needed=10)
    name_a = map(get_name, rpages_a)
    name_s = map(get_name, rpages_s)
    facebook_links_a = map(get_facebook_link, rpages_a)
    twitter_links_a = map(get_facebook_link, rpages_a)
    facebook_links_s = map(get_twitter_link, rpages_s)
    twitter_links_s = map(get_twitter_link, rpages_s)
    fb_pic_a = map(get_facebook_pic, rpages_a)
    fb_pic_s = map(get_facebook_pic, rpages_s)
    template = loader.get_template('recommended.html')
    context = RequestContext(request,
                             {'recommended_actual_age': zip(name_a, facebook_links_a, twitter_links_a, fb_pic_a),
                              'recommended_social_age': zip(name_s, facebook_links_s, twitter_links_s, fb_pic_s),
                              }
                             )

    return HttpResponse(template.render(context))


def analysis(request):
    user_id = request.GET.get('id', 0)
    if user_id == 0:
        user_id = request.session['user_id']
    user = models.User.objects.get(id=user_id)
    if user is None:
        return redirect('index')
    # get all the tested pages of the users, compute the average age of these pages
    # and the approximate weighting of them based on total sample from a page
    tested_fb_page = user.liked_pages.all().filter(page__total__gte=20)
    tested_fb_page = list(map(lambda x: x.page, tested_fb_page))
    tested_tw_page = user.followed_pages.all().filter(page__total__gte=20)
    tested_tw_page = list(map(lambda x: x.page, tested_tw_page))

    # get the computed average ages
    f = lambda x: int(x.avg_age)
    fb_avg_age = map(f, tested_fb_page)
    tw_avg_age = map(f, tested_tw_page)
    # get the approximate weighting
    g = lambda x: x.total
    fb_page_frac = list(map(g, tested_fb_page))
    tw_page_frac = list(map(g, tested_tw_page))
    sfb = sum(fb_page_frac)
    stw = sum(tw_page_frac)
    fb_page_frac = list(map(lambda x: x / sfb, fb_page_frac))
    tw_page_frac = list(map(lambda x: x / stw, tw_page_frac))
    h = lambda x: format(x * 100, '.2f')
    fb_page_percent = map(h, fb_page_frac)
    tw_page_percent = map(h, tw_page_frac)
    # get the profile pic
    fb_page_pic = map(get_facebook_pic, tested_fb_page)
    tw_page_pic = map(get_twitter_pic, tested_tw_page)
    # get the name
    fb_page_handle = map(lambda x: x.fb_handle, tested_fb_page)
    tw_page_handle = map(lambda x: x.tw_handle, tested_tw_page)

    template = loader.get_template('analysis.html')
    context = RequestContext(request, {'fb_data': zip(fb_page_pic, fb_page_handle, fb_avg_age, fb_page_percent),
                                       'tw_data': zip(tw_page_pic, tw_page_handle, tw_avg_age, tw_page_percent),
                                       }
                             )

    return HttpResponse(template.render(context))


def friends(request):
    user_id = request.GET.get('id', 0)
    if user_id == 0:
        user_id = request.session['user_id']
    user = models.User.objects.get(id=user_id)
    if user is None:
        return redirect('index')
    # Get the users' facebook friends who have used our app, get their pic, name, age and social age to create
    # a comparison chart on the webpage.
    friend_ids = user.fb_friends
    friends = []
    friends.append(user)
    for id in friend_ids.split(','):
        try:
            friend = models.User.objects.get(fb_id=id)
            friends.append(friend)
        except:
            pass

    friends_pic = map(lambda x: "http://graph.facebook.com/" + x.fb_id + "/picture?type=square", friends)
    friends_name = map(lambda x: x.name, friends)
    friends_age = map(lambda x: age_from_birthday(x.birthday), friends)
    friends_sage = map(lambda x: x.social_age, friends)

    template = loader.get_template('friends.html')
    context = RequestContext(request, {'friends_data': zip(friends_pic, friends_name, friends_age, friends_sage),
                                       'has_friend': 1 if len(friends) != 0 else 0,
                                       'logged_in_fb': 1 if user.fb_id != -1 else 0,
                                       }
                             )

    return HttpResponse(template.render(context))


def graphs(request):
    template = loader.get_template('results_graphs.html')
    context = RequestContext(request, {})
    # return redirect('twitter_results')
    return HttpResponse(template.render(context))


def graph_data(request):
    user_id = request.GET.get('id', 0)
    if user_id == 0:
        user_id = request.session['user_id']
    user = models.User.objects.get(id=user_id)
    if user is None:
        return JsonResponse({})

    # Liked Page vs Age
    liked_page_data = []
    for f in user.liked_pages.all():
        if f.page.total > 5:
            liked_page_data.append([f.page.name, f.page.avg_age])
    for f in user.followed_pages.all():
        if f.page.total > 5:
            liked_page_data.append([f.page.name, f.page.avg_age])
    print(liked_page_data)
    liked_page_data = [list(x) for x in set(tuple(x) for x in liked_page_data)]
    liked_page_data = sorted(liked_page_data, key=lambda x: x[1])

    # Social age distribution for user biological age
    bio_dist_data = age_table.age_table_bio_dist(user.age)
    bio_dist_data = list(filter(lambda x: x[1] > 0, bio_dist_data))

    # Biological age distribution for user social age
    soc_dist_data = age_table.age_table_soc_dist(user.social_age)
    soc_dist_data = list(filter(lambda x: x[1] > 0, soc_dist_data))

    return JsonResponse({"page_age": [["Page", "Average Age"]] + liked_page_data,
                         "bio_dist": [["Social Age", "Frequency"]] + bio_dist_data, "bio_age": user.age,
                         "soc_dist": [["Biological Age", "Frequency"]] + soc_dist_data, "soc_age": user.social_age})


# =====================================================================================================
# ======================================= Util functions ==============================================
# =====================================================================================================

def age_from_birthday(birthday):
    return int((date.today() - birthday.date()).days / 365.2425)


def fb_pages_from_user(user):
    return list(map(lambda x: x.page.fb_id, user.liked_pages.all()))


def tw_pages_from_user(user):
    return list(map(lambda x: x.page.fb_id, user.followed_pages.all()))


def get_name(page):
    return page.name


def get_facebook_link(page):
    return "https://www.facebook.com/" + page.fb_handle


def get_twitter_link(page):
    return "https://www.twitter.com/" + page.tw_handle


def get_facebook_pic(page):
    return "http://graph.facebook.com/" + page.fb_id + "/picture?type=square"


def get_twitter_pic(page):
    return "https://twitter.com/" + page.tw_handle + "/profile_image?size=normal"


def gen_message(bio_age, social_age):
    age_diff = bio_age - social_age
    if bio_age == 0:
        msg = "Sign in with facebook as well to get your actual age so we can give you a more in depth result!"
    elif social_age == -1:
        msg = "Sorry the pages you have liked or followed are insufficient for us to predict your social age! Maybe try logging in with the other social network?"
    elif age_diff < -15:
        msg = "This is a msg for <-15"
    elif age_diff >= -15 & age_diff <= -6:
        msg = "This is a msg for -6~-15"
    elif age_diff >= -5 & age_diff <= 5:
        msg = "This is a msg for -5~+5"
    elif age_diff >= 6 & age_diff <= 15:
        msg = "This is a msg for +6~+15"
    elif age_diff > 15:
        msg = "This is a msg for >+15"
    return msg
