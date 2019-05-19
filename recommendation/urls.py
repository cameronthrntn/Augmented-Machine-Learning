from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'recommendation'
urlpatterns = [
    path('', views.index, name='index'),
    url(r'^movie/search', views.movie, name='movie'),
]