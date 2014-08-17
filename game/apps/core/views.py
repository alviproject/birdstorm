import blinker
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http.response import HttpResponse
from game.apps.core import models
from game.apps.core.models.planet.models import TerrestrialPlanet
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from game.utils.async_action import async_action
import game.apps.core.signals
from django.conf import settings
from blinker import signal


class Ships(viewsets.ReadOnlyModelViewSet):
    model = models.Ship
    serializer_class = models.ShipSerializer


class Systems(viewsets.ReadOnlyModelViewSet):
    model = models.System
    serializer_class = models.SystemSerializer

    def retrieve(self, request, pk=None, *args, **kwargs):
        system = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = models.SystemDetailsSerializer(system, context=dict(request=request))
        return Response(serializer.data)


class Planets(viewsets.ReadOnlyModelViewSet):
    model = models.Planet
    serializer_class = models.PlanetSerializer

    def retrieve(self, request, pk=None, *args, **kwargs):
        planet = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = models.PlanetDetailsSerializer(planet, context=dict(request=request))
        return Response(serializer.data)


class OwnShips(viewsets.ReadOnlyModelViewSet):
    serializer_class = models.OwnShipSerializer

    def get_queryset(self, request):
        return models.Ship.objects.filter(owner=request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)
        object_list = self.filter_queryset(queryset)
        page = self.paginate_queryset(object_list)
        serializer = self.get_pagination_serializer(page)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        ship = get_object_or_404(self.get_queryset(request), pk=pk)
        serializer = models.OwnShipDetailsSerializer(ship, context=dict(request=request))
        return Response(serializer.data)

    @async_action
    def move(self, request, pk=None):
        system_id = request.DATA['system_id']
        system = models.System.objects.get(pk=system_id)
        ship = self.get_queryset(request).get(pk=pk)
        time = 5  # seconds
        with ship.lock():
            ship.system = system
            ship.save()
            signal_name = game.apps.core.signals.ship_move
            blinker.signal(signal_name % 'main').send(ship, time=time)
            yield time
        return Response()

    @async_action
    def scan(self, request, pk=None):
        planet_id = request.DATA['planet_id']
        level = int(request.DATA['level'])
        request_id = request.META['HTTP_X_REQUESTID']
        planet = models.Planet.objects.get(pk=planet_id)
        ship = self.get_queryset(request).get(pk=pk)
        user = ship.owner
        scan_progress_signal = blinker.signal(game.apps.core.signals.planet_scan_progress % request_id)

        with ship.lock():
            results = user.profile.scan_results(planet_id)
            if level < 0 or level >= len(results):
                level = len(results)
            #TODO check why we have to pass self as a first argument
            scan_progress_signal.send(self, message=dict(
                type="info",
                text="Scanning level %d, please stand by..." % level,
            ))

            yield pow(settings.FACTOR, level)

            if ship.system != planet.system:
                scan_progress_signal.send(self, message=dict(
                    type="error",
                    text="Current ship is not located next to the scanned planet.",
                ))
                return

            if not isinstance(planet, TerrestrialPlanet):
                scan_progress_signal.send(self, message=dict(
                    type="error",
                    text="This planet type is not supported by equipped scanner.",
                ))
                return

            if user.profile.is_drilled(planet_id):
                scan_progress_signal.send(self, message=dict(
                    type="error",
                    text="Planet was already drilled, you have to wait some time before net extraction.",
                ))
                return

            if level >= 2:
                scan_progress_signal.send(self, message=dict(
                    type="error",
                    text="Equipped scanner cannot scan any deeper.",
                ))
                return

            try:
                level_resources = planet.data['resources'][level]
            except IndexError:
                scan_progress_signal.send(self, message=dict(
                    type="error",
                    text="Some solid structures below surface of this planet block deeper scans.",
                ))
                return
            current_level_result = []
            for r in level_resources:
                current_level_result.append(dict(
                    type=r['type'],
                    quantity=r['quantity'],
                ))
            scan_progress_signal.send(
                self,
                results=current_level_result,
                level=level,
                message=dict(
                    type="success",
                    text="Scan successful",
                ),
            )

            user.profile.set_scan_result(planet_id, level, current_level_result)
            user.profile.save()


def test_view(request):
    user = User.objects.get(pk=1)
    user = authenticate(user=user)
    login(request, user)
    return HttpResponse("ok")

