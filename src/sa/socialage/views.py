from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
from django.template import RequestContext, loader
import json
import urllib.request

from . import models

APP_ID = 507982369367860
APP_SECRET = "213bdd72e269941abce42d09f8908765"


def index(request):
    print(request.GET)
    if not request.GET:
        request.session['index_uri'] = request.build_absolute_uri()
        return redirect("https://graph.facebook.com/oauth/authorize?client_id=" + str(APP_ID) + "&redirect_uri=" + request.session.get('index_uri') + "&scope=user_likes,user_birthday,user_friends")
    else:
        if request.GET.get('error_message'):
            return JsonResponse(request.GET)
        else:
            code = request.GET.get("code")
            token_request_url = "https://graph.facebook.com/v2.5/oauth/access_token?client_id=" + str(APP_ID) + "&redirect_uri=" + request.session.get('index_uri') + "&client_secret=" + APP_SECRET + "&code=" + code
            token = http_get(token_request_url)
            request.session['access_token'] = token['access_token']
            user = http_get("https://graph.facebook.com/me?access_token=" + request.session.get('access_token'))
            request.session['user'] = user
            try:
                facebook_user = models.FacebookUser.objects.get(id=user['id'])
            except: 
                facebook_user = None
            if facebook_user is None:
                facebook_user = models.FacebookUser.objects.create(id=user['id'],name=user['name'])
            liked_pages = http_get("https://graph.facebook.com/" + user['id'] + "/likes/?access_token=" + request.session.get('access_token'))
            pages_liked = []
            for p in liked_pages['data']:
                try:
                    page = models.FacebookPage.objects.get(id=p['id'])
                except:
                    page = None
                if page is None:
                    page = models.FacebookPage.objects.create(id=p['id'],name=p['name'])
                page_like_time = datetime.strptime(p['created_time'], '%Y-%m-%dT%H:%M:%S%z')
                page_like = models.FacebookPageLike.objects.create(user=facebook_user,page=page,time=page_like_time)
                pages_liked.append(page_like)
            template = loader.get_template('likes.html')
            context = RequestContext(request, {'pages_liked': pages_liked})
            return HttpResponse(template.render(context))    
     
     
def test(request):
    return JsonResponse({})
    
    
def http_get(url):
    request = urllib.request.urlopen(url)
    response = json.loads(request.read().decode("utf-8"))
    return response