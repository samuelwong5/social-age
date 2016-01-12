from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^facebook/', views.facebook, name='facebook'),
    url(r'^fb_results/', views.fb_results, name='fb_results'),
    url(r'^results/', views.results, name='results'),
    url(r'^twitter/', views.twitter, name='twitter'),
    url(r'^tw_results/', views.twitter_results, name='twitter_results'),
    url(r'^fb_api/', views.fb_api, name='fb_api'),
    url(r'^recommended/', views.recommended, name='recommended'),
    url(r'^analysis/', views.analysis, name='analysis'),
    url(r'^graphs/', views.graphs, name='graphs'),
    url(r'^graph_data/', views.graph_data, name='graph_data'),
]