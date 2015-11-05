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


def index(request):
    if not request.GET: # New session - Facebook authentication
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
                        page = models.FacebookPage.objects.get(id=p['id'])
                    except:
                        page = None
                    if page is None:
                        page = models.FacebookPage.objects.create(id=p['id'],name=p['name'])
                    page_like_time = datetime.strptime(p['created_time'], '%Y-%m-%dT%H:%M:%S%z')
                    page_like = models.FacebookPageLike.objects.create(user=facebook_user,page=page,time=page_like_time)
                curr_page = http_get(next_page)
            return redirect('results')   
     

def results(request):
    liked_pages = {}
    try:
        facebook_user = models.FacebookUser.objects.get(id=request.session.get('user')['id'])
        liked_pages = facebook_user.liked_pages.all()
    except: 
        pass
    template = loader.get_template('results.html')
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
