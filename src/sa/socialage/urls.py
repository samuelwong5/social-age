from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^facebook/', views.facebook, name='facebook'),
    url(r'^fb_results/', views.fb_results, name='fb_results'),
    url(r'^results/', views.results, name='results'),
    url(r'^test/', views.test, name='test'),
    #url(r'^import/', views.import_csv, name='import_csv'),
    url(r'^twitter/', views.twitter, name='twitter'),
    url(r'^tw_results/', views.twitter_results, name='twitter_results'),
    url(r'^fb_api/', views.fb_api, name='fb_api'),

]