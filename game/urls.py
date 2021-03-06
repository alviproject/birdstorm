from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.models import User
from rest_framework import routers
import game.apps.account.views
import game.apps.core.views
import game.apps.chat.views

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'users', game.apps.account.views.Users)
router.register(r'accounts', game.apps.account.views.Users)
router.register(r'core/buildings', game.apps.core.views.Buildings)
router.register(r'core/systems', game.apps.core.views.Systems)
router.register(r'core/planets', game.apps.core.views.Planets)
router.register(r'core/tasks', game.apps.core.views.Tasks)
router.register(r'chat/messages', game.apps.chat.views.Messages)


urlpatterns = patterns(
    '',
    url(r'^', include('game.apps.account.urls')),
    url(r'^', include('game.apps.core.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api/account$', game.apps.account.views.Account.as_view()),  # TODO not shown at /api
    url(r'^api/core/base/next_turn/$', game.apps.core.views.next_turn),  # TODO not shown at /api
    url(r'^api/account/register', 'game.apps.account.views.register'),  # TODO
    url(r'^api/account/login', 'game.apps.account.views.login'),  # TODO
    url(r'^forum/', include('pybb.urls', namespace='pybb')),
    url(r'^section/about', 'game.apps.core.views.section', {'name': 'about'}),
    url(r'^map/*', 'game.apps.core.views.index'),
    url(r'^account/signup', 'game.apps.core.views.index'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
