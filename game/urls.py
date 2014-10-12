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
router.register(r'core/ships', game.apps.core.views.Ships)
router.register(r'core/buildings', game.apps.core.views.Buildings)
router.register(r'core/systems', game.apps.core.views.Systems)
router.register(r'core/planets', game.apps.core.views.Planets)
router.register(r'core/tasks', game.apps.core.views.Tasks)
router.register(r'core/own_ships', game.apps.core.views.OwnShips, base_name='own_ships')
router.register(r'chat/messages', game.apps.chat.views.Messages)


urlpatterns = patterns(
    '',
    url(r'^', include('game.apps.account.urls')),
    url(r'^', include('game.apps.core.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api/account$', game.apps.account.views.Account.as_view(model=User)),  # TODO not shown at /api
    url(r'^api/account/register', 'game.apps.account.views.register'),  # TODO
    url(r'^forum/', include('pybb.urls', namespace='pybb')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
