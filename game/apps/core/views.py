import blinker
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.shortcuts import render
from django.template.context import RequestContext
from game.apps.account.models import AccountSerializer
from game.apps.core import models
from game.apps.core.models.planet.models import TerrestrialPlanet
from game.apps.core.models.planet.serializers import PlanetDetailsSerializer
from game.apps.core.models.ships import Ship
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from game.utils.async_action import async_action
import game.apps.core.signals
from django.conf import settings


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
        user = request.user
        signal_id = "%d_%s" % (planet_id, request_id)
        scan_progress_signal = blinker.signal(game.apps.core.signals.planet_actions_progress % signal_id)

        with ship.lock():
            results = user.profile.get_scan_results(planet_id)
            if level < 0 or level >= len(results):
                level = len(results)
            #TODO check why we have to pass self as a first argument
            scan_progress_signal.send(self, message=dict(
                type="info",
                text="Scanning level %d, please stand by..." % level,
            ))

            if ship.system != planet.system:
                scan_progress_signal.send(self, message=dict(
                    type="error",
                    text="Current ship is not located next to the scanned planet.",
                ))
                return

            yield pow(settings.FACTOR, level)

            if not isinstance(planet, TerrestrialPlanet):
                scan_progress_signal.send(self, message=dict(
                    type="error",
                    text="This planet type is not supported by equipped scanner.",
                ))
                return

            if user.profile.is_drilled(planet_id):
                scan_progress_signal.send(self, message=dict(
                    type="error",
                    text="Planet was already drilled, you have to wait some time before next scan.",
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
            except (IndexError, KeyError):
                scan_progress_signal.send(self, message=dict(
                    type="error",
                    text="Some solid structures below surface of this planet block deeper scans.",
                ))
                return
            current_level_result = {}
            for type, quantity in level_resources.items():
                current_level_result[type] = quantity
            scan_progress_signal.send(self, level=level, message=dict(type="success", text="Scan successful", ), )

            user.profile.set_scan_result(planet_id, level, current_level_result)
            user.profile.save()

            signal_id = "%d_%s" % (planet_id, request_id)
            planet_details_signal = blinker.signal(game.apps.core.signals.planet_details % signal_id)
            planet_details_signal.send(self, planet=PlanetDetailsSerializer(planet, context=dict(request=request)).data)

    @async_action
    def extract(self, request, pk=None):
        planet_id = request.DATA['planet_id']
        level = int(request.DATA['level'])
        resource_type = request.DATA['resource_type']
        request_id = request.META['HTTP_X_REQUESTID']
        planet = models.Planet.objects.get(pk=planet_id)
        ship = self.get_queryset(request).get(pk=pk)
        user = request.user
        signal_id = "%d_%s" % (planet_id, request_id)
        scan_progress_signal = blinker.signal(game.apps.core.signals.planet_actions_progress % signal_id)

        with ship.lock():
            results = user.profile.get_scan_results(planet_id)
            if level < 0 or level >= len(results):
                raise RuntimeError("Wrong level")

            scan_progress_signal.send(self, message=dict(
                type="info",
                text="Extracting %s, please stand by..." % resource_type,
            ))

            if ship.system != planet.system:
                scan_progress_signal.send(self, message=dict(
                    type="error",
                    text="Current ship is not located next to the scanned planet.",
                ))
                return

            yield pow(settings.FACTOR, level*2)

            if user.profile.is_drilled(planet_id):
                scan_progress_signal.send(self, message=dict(
                    type="error",
                    text="Planet was already drilled, you have to wait some time before next extraction.",
                ))
                return

            if level >= 2:
                scan_progress_signal.send(self, message=dict(
                    type="error",
                    text="Equipped drill cannot scan any deeper.",
                ))
                return

            resources = results[level]
            ship.add_resource(resource_type, resources[resource_type])
            ship.save()
            scan_progress_signal.send(
                self,
                message=dict(
                    type="success",
                    text="Extraction successful",
                ),
            )
            user.profile.add_drilled_planet(planet_id)
            user.profile.save()

            signal_id = "%d_%s" % (planet_id, request_id)
            planet_details_signal = blinker.signal(game.apps.core.signals.planet_details % signal_id)
            planet_details_signal.send(self, planet=PlanetDetailsSerializer(planet, context=dict(request=request)).data)


class Buildings(viewsets.ReadOnlyModelViewSet):
    model = models.Building
    serializer_class = models.BuildingSerializer

    #TODO this shall be Port method
    @action()
    def buy(self, request, pk=None):
        #TODO check if ship is at the right system
        user = request.user
        ship_id = request.DATA['ship_id']
        resource = request.DATA['resource']
        quantity = int(request.DATA['quantity'])
        request_id = request.META['HTTP_X_REQUESTID']
        port = self.get_queryset().get(pk=pk)
        price = port.prices[resource]['sale_price']
        ship = request.user.ship_set.get(pk=ship_id)

        quantity = min(quantity, port.resources.get(resource, 0))
        quantity = min(quantity, user.credits//price)
        cost = price * quantity
        ship.add_resource(resource, quantity)
        port.remove_resource(resource, quantity)
        ship.save()
        user.credits -= cost
        user.save()
        port.save()

        account_signal = blinker.signal(game.apps.core.signals.account_data % user.id)
        account_signal.send(None, data=AccountSerializer(user).data)
        signal_id = "%d_%s" % (port.planet_id, request_id)
        actions_signal = blinker.signal(game.apps.core.signals.planet_actions_progress % signal_id)
        actions_signal.send(
            self,
            message=dict(
                type="success",
                text="Bought %d of %s. Total cost: %d" % (quantity, resource, cost),
            ),
        )

        signal_id = "%d_%s" % (port.planet_id, request_id)
        planet_details_signal = blinker.signal(game.apps.core.signals.planet_details % signal_id)
        planet_details_signal.send(self, planet=PlanetDetailsSerializer(port.planet, context=dict(request=request)).data)

        return Response()

    #TODO this shall be Port method
    @action()
    def sell(self, request, pk=None):
        #TODO check if ship is at the right system
        user = request.user
        ship_id = request.DATA['ship_id']
        resource = request.DATA['resource']
        quantity = int(request.DATA['quantity'])
        request_id = request.META['HTTP_X_REQUESTID']
        port = self.get_queryset().get(pk=pk)
        price = port.prices[resource]['purchase_price']
        ship = request.user.ship_set.get(pk=ship_id)

        quantity = min(quantity, ship.resources.get(resource, 0))
        cost = price * quantity
        ship.remove_resource(resource, quantity)
        port.add_resource(resource, quantity)
        ship.save()
        user.credits += cost
        user.save()
        port.save()

        account_signal = blinker.signal(game.apps.core.signals.account_data % user.id)
        account_signal.send(None, data=AccountSerializer(user).data)

        signal_id = "%d_%s" % (port.planet_id, request_id)
        actions_signal = blinker.signal(game.apps.core.signals.planet_actions_progress % signal_id)
        actions_signal.send(
            self,
            message=dict(
                type="success",
                text="Sold %d of %s. Total profit: %d" % (quantity, resource, cost),
            ),
        )

        signal_id = "%d_%s" % (port.planet_id, request_id)
        planet_details_signal = blinker.signal(game.apps.core.signals.planet_details % signal_id)
        planet_details_signal.send(self, planet=PlanetDetailsSerializer(port.planet, context=dict(request=request)).data)

        return Response()

    #TODO this shall be Provider method
    @async_action
    def order(self, request, pk=None):
        #TODO check if ship is at the right system
        user = request.user
        ship_id = request.DATA['ship_id']
        order = request.DATA['order']
        quantity = int(request.DATA['quantity'])
        request_id = request.META['HTTP_X_REQUESTID']
        building = self.get_queryset().get(pk=pk)
        ship = user.ship_set.get(pk=ship_id)

        for delay in building.order(order, quantity, ship, user, request_id):
            yield delay


def test_view(request):
    ship = Ship.objects.get(pk=1)
    ship.system_id = 1
    ship.save()
    return HttpResponse("ok")


def index(request):
    context = RequestContext(request, {
    })
    return render(request, 'index.html', context_instance=context)
