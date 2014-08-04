from django.conf.urls import patterns, include
from django.conf.urls import url


urlpatterns = patterns(
    '',
    url(r'^test/', 'game.apps.core.views.test_view'),  # TODO remove in prod
)
