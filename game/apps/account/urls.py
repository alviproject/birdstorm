from django.conf.urls import patterns
from django.conf.urls import url


#TODO remove?
urlpatterns = patterns(
    '',
    url(r'^account/register', 'game.apps.account.views.register'),
    url(r'^account/logout/$', 'django.contrib.auth.views.logout'),
)