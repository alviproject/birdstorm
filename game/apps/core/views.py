import blinker
from django.core.exceptions import ValidationError
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.template.context import RequestContext
from game.apps.account.models import AccountSerializer
from game.apps.core import models
from game.apps.core import serializers
from game.apps.core.models.planet.models import TerrestrialPlanet, GasGiant
from game.apps.core.serializers.buildings import BuildingSerializer
from game.apps.core.serializers.planet import PlanetDetailsSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from game.utils.async_action import async_action
import game.apps.core.signals
from django.conf import settings


def check_planet(ship, planet_id):
    if ship.planet_id != planet_id:
        messages = blinker.signal(game.apps.core.signals.messages % ship.owner_id)
        messages.send(None, message=dict(
            type="error",
            text='Your ship is not located at this planet.',
        ))
        raise RuntimeError


class Ships(viewsets.ReadOnlyModelViewSet):
    model = models.Ship
    serializer_class = serializers.ShipSerializer


class Systems(viewsets.ReadOnlyModelViewSet):
    model = models.System
    serializer_class = serializers.SystemSerializer

    def retrieve(self, request, pk=None, *args, **kwargs):
        system = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = serializers.SystemDetailsSerializer(system, context=dict(request=request))
        return Response(serializer.data)


class Planets(viewsets.ReadOnlyModelViewSet):
    model = models.Planet
    serializer_class = serializers.PlanetSerializer

    def retrieve(self, request, pk=None, *args, **kwargs):
        planet = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = serializers.PlanetDetailsSerializer(planet, context=dict(request=request))
        return Response(serializer.data)


class OwnShips(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.OwnShipSerializer

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
        serializer = serializers.OwnShipDetailsSerializer(ship, context=dict(request=request))
        return Response(serializer.data)

    @async_action
    def move(self, request, pk=None):
        planet_id = request.DATA['planet_id']
        planet = models.Planet.objects.get(pk=planet_id)
        ship = self.get_queryset(request).get(pk=pk)
        time = 5  # seconds
        with ship.lock():
            ship.planet = planet
            ship.save()
            signal_name = game.apps.core.signals.ship_move
            blinker.signal(signal_name % 'main').send(ship, time=time)
            yield time
        return Response()

    @async_action
    def scan(self, request, pk=None):
        planet_id = request.DATA['planet_id']
        request_id = request.META['HTTP_X_REQUESTID']
        planet = models.Planet.objects.get(pk=planet_id)
        ship = self.get_queryset(request).get(pk=pk)
        user = request.user
        messages = blinker.signal(game.apps.core.signals.messages % user.id)

        check_planet(ship, planet.id)

        if isinstance(planet, GasGiant):
            messages.send(self, message=dict(
                type="error",
                text="This planet type is not supported by equipped scanner.",
            ))
            return

        if user.profile.is_drilled(planet_id):
            messages.send(self, message=dict(
                type="error",
                text="Planet was already drilled, you have to wait some time before next scan.",
            ))
            return

        with ship.lock():
            results = user.profile.scan_results.get(planet_id, [])
            level = len(results)

            while True:
                #TODO check why we have to pass self as a first argument
                messages.send(self, message=dict(
                    type="info",
                    text="Scanning level %d, please stand by..." % level,
                ))

                if level >= ship.scanner.deepness():
                    messages.send(self, message=dict(
                        type="error",
                        text="Equipped scanner cannot scan any deeper.",
                    ))
                    break

                yield pow(settings.FACTOR, level)

                try:
                    level_resources = planet.data['resources'][level]
                except (IndexError, KeyError):
                    messages.send(self, message=dict(
                        type="error",
                        text="Some solid structures below surface of this planet block deeper scans.",
                    ))
                    break
                current_level_result = {}
                for type, quantity in level_resources.items():
                    current_level_result[type] = quantity

                user.profile.set_scan_result(planet_id, level, current_level_result)
                messages.send(self, level=level, message=dict(type="success", text="Scan successful", ), )

                signal_id = "%d_%s" % (planet_id, request_id)
                planet_details_signal = blinker.signal(game.apps.core.signals.planet_details % signal_id)
                planet_details_signal.send(self, planet=PlanetDetailsSerializer(planet, context=dict(request=request)).data)

                level += 1

            user.profile.save()

            blinker.signal(game.apps.core.signals.planet_scan % user.id).send()

    @async_action
    def extract(self, request, pk=None):
        planet_id = request.DATA['planet_id']
        level = int(request.DATA['level'])
        resource_type = request.DATA['resource_type']
        request_id = request.META['HTTP_X_REQUESTID']
        planet = models.Planet.objects.get(pk=planet_id)
        ship = self.get_queryset(request).get(pk=pk)
        user = request.user
        messages = blinker.signal(game.apps.core.signals.messages % user.id)

        with ship.lock():
            results = user.profile.scan_results.get(planet_id, [])
            if level < 0 or level >= len(results):
                raise RuntimeError("Wrong level")

            messages.send(self, message=dict(
                type="info",
                text="Extracting %s, please stand by..." % resource_type,
            ))

            check_planet(ship, planet.id)

            if user.profile.is_drilled(planet_id):
                messages.send(self, message=dict(
                    type="error",
                    text="Planet was already drilled, you have to wait some time before next extraction.",
                ))
                return

            if level >= ship.drill.deepness():
                messages.send(self, message=dict(
                    type="error",
                    text="Equipped drill cannot drill so deep.",
                ))
                return

            yield pow(settings.FACTOR, level*2)

            resources = results[level]
            ship.add_resource(resource_type, resources[resource_type])
            ship.save()
            messages.send(
                self,
                message=dict(
                    type="success",
                    text="Extraction successful, resources were added to your ship cargo.",
                ),
            )
            user.profile.add_drilled_planet(planet_id)
            user.profile.save()

            signal_id = "%d_%s" % (planet_id, request_id)
            planet_details_signal = blinker.signal(game.apps.core.signals.planet_details % signal_id)
            planet_details_signal.send(self, planet=PlanetDetailsSerializer(planet, context=dict(request=request)).data)

            blinker.signal(game.apps.core.signals.planet_extract % user.id).send(ship=ship)


class Buildings(viewsets.ReadOnlyModelViewSet):
    model = models.Building
    serializer_class = serializers.BuildingSerializer

    #TODO this shall be Port method
    @action()
    def buy(self, request, pk=None):
        user = request.user
        ship_id = request.DATA['ship_id']
        resource = request.DATA['resource']
        quantity = int(request.DATA['quantity'])
        request_id = request.META['HTTP_X_REQUESTID']
        port = self.get_queryset().get(pk=pk)
        price = port.prices[resource]['sale_price']
        ship = request.user.ship_set.get(pk=ship_id)

        check_planet(ship, port.planet_id)

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
        messages = blinker.signal(game.apps.core.signals.messages % signal_id)
        messages.send(
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
        user = request.user
        ship_id = request.DATA['ship_id']
        resource = request.DATA['resource']
        quantity = int(request.DATA['quantity'])
        request_id = request.META['HTTP_X_REQUESTID']
        port = self.get_queryset().get(pk=pk)
        price = port.prices[resource]['purchase_price']
        ship = request.user.ship_set.get(pk=ship_id)

        check_planet(ship, port.planet_id)

        quantity = min(quantity, ship.resources.get(resource, 0))
        cost = price * quantity
        ship.remove_resource(resource, quantity)
        #port.add_resource(resource, quantity)
        ship.save()
        user.profile.credits += cost
        user.profile.save()
        #port.save()

        account_signal = blinker.signal(game.apps.core.signals.account_data % user.id)
        account_signal.send(None, data=AccountSerializer(user, context={'request': request}).data)

        messages = blinker.signal(game.apps.core.signals.messages % user.id)
        messages.send(
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
        user = request.user
        ship_id = request.DATA['ship_id']
        order = request.DATA['order']
        quantity = int(request.DATA['quantity'])
        request_id = request.META['HTTP_X_REQUESTID']
        building = self.get_queryset().get(pk=pk)
        ship = user.ship_set.get(pk=ship_id)

        check_planet(ship, building.planet_id)

        for delay in building.order(order, quantity, ship, user, request_id):
            yield delay
            #TODO consider sending this signal after all units are produced
            blinker.signal(game.apps.core.signals.order % user.id).send(ship=ship)

    #TODO this shall be Workshop method
    # alternatively this can be a separate resource aligned with ship like /core/own_ships/2/workshop_storage
    # same for other similar cases like planet.scan_results
    @action()
    def analyze(self, request, pk=None):
        #TODO check if ship is at the right system
        user = request.user
        building = self.get_queryset().get(pk=pk)
        ship_id = request.DATA['ship_id']
        ship = user.ship_set.get(pk=ship_id)
        result = building.processes(ship)
        return Response(result)

    #TODO this shall be Warehouse method
    @action()
    def store(self, request, pk=None):
        user = request.user
        ship_id = request.DATA['ship_id']
        resource = request.DATA['resource']
        action = request.DATA['action']
        quantity = int(request.DATA['quantity'])
        #request_id = request.META['HTTP_X_REQUESTID']
        warehouse = self.get_queryset().get(pk=pk)
        ship = request.user.ship_set.get(pk=ship_id)

        check_planet(ship, warehouse.planet_id)
        container = warehouse.get_resource_container(user)

        if action == "unload":
            quantity = min(quantity, ship.resources[resource])
            ship.remove_resource(resource, quantity)
            container.add_resource(resource, quantity)
        else:
            quantity = min(quantity, container.resources[resource])
            ship.add_resource(resource, quantity)
            container.remove_resource(resource, quantity)
        ship.save()
        user.save()
        user.profile.save()

        signal_id = "%d_%d" % (warehouse.id, user.id)
        signal = blinker.signal(game.apps.core.signals.building_user % signal_id)
        signal.send(self, building=BuildingSerializer(warehouse, context=dict(request=request)).data)

        return Response()


class Tasks(viewsets.ReadOnlyModelViewSet):
    model = models.Task
    serializer_class = serializers.TaskSerializer

    def get_queryset(self, request):
        if request.user.is_authenticated():
            return models.Task.objects.filter(user=request.user, archived=False)
        else:
            return models.Task.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)
        object_list = self.filter_queryset(queryset)
        page = self.paginate_queryset(object_list)
        serializer = self.get_pagination_serializer(page)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        task = get_object_or_404(self.get_queryset(request), pk=pk)
        serializer = serializers.TaskSerializer(task, context=dict(request=request))
        return Response(serializer.data)

    @action()
    def action(self, request, pk=None):
        task = models.Task.objects.get(pk=pk)
        try:
            task.action(request.DATA)
        except ValidationError as x:
            return Response(x.message, status=HttpResponseBadRequest.status_code)

        return Response()


#TODO remove
def test_view(request):
    #ship = Ship.objects.get(pk=1)
    #ship.system_id = 1
    #ship.save()
    return HttpResponse("ok")


def index(request):
    context = RequestContext(request, {
    })
    return render(request, 'index.html', context_instance=context)
