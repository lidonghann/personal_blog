"""Personal_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import views

urlpatterns = [
    url(r'^login/', views.login),
    url(r'^logout/', views.logout),
    url(r'^index/', views.index),
    url(r'^register/', views.register),
    url(r'^is_exist/', views.check_user_is_exist),
    url(r'^about/', views.about),
    url(r'^whole_passage/', views.whole_passage),
    url(r'^all_article/', views.all_article),
    url(r'^comment/', views.comment),
    url(r'^children_comment/', views.comment),
    url(r'^saying/', views.saying),
    url(r'^tag/', views.tag),
    url(r'^personal_center/', views.personal_center),
    url(r'^msg_board/', views.msg_board),
    url(r'^user_blog/', views.user_blog),
    url(r'^msg_update/', views.msg_update),
    url(r'^children_msg/', views.msg_update),
    url(r'^news_spider/', views.news_spider),
    url(r'^video/(.+)/$', views.video),
    url(r'^video_detailed/', views.video_detailed),
    url(r'^all_music/', views.all_music),
    url(r'^music/', views.music),
    url(r'^music_singer/', views.find_songs_from_singer),
    url(r'^search_mus/', views.search_mus),
    url(r'^search_video/(.+)/$', views.search_video),
    url(r'^search_blog/', views.search_blog),
    url(r'^search_say/', views.search_say),
    url(r'^search_news/', views.search_news),
    url(r'^video_com/', views.video_comment),
    url(r'^children_com/', views.video_comment),
    url(r'^wangyi_news/(.+)/$', views.wangyi_news),
    url(r'^search_wangyi_news/(.+)/$', views.search_wangyi_news),
    url(r'^weather_forecast/', views.weather_forecast),
]
