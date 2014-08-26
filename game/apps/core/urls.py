from django.conf.urls import patterns, include
from django.conf.urls import url


urlpatterns = patterns(
    '',
    url(r'^$', 'game.apps.core.views.index'),
    url(r'^test/', 'game.apps.core.views.test_view'),  # TODO remove in prod
)
