import blinker
from django.core.exceptions import ValidationError
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.template.context import RequestContext
from game.apps.account.models import AccountSerializer
from game.apps.core import models
from game.apps.core import serializers
from game.apps.core.models.planet.models import GasGiant
from game.apps.core.serializers.buildings import BuildingSerializer
from game.apps.core.serializers.planet import PlanetDetailsSerializer
from rest_framework import viewsets
from rest_framework.decorators import api_view, list_route, detail_route
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


class Systems(viewsets.ReadOnlyModelViewSet):
    model = models.System
    serializer_class = serializers.SystemSerializer
    queryset = models.System.objects.all()


def retrieve(self, request, pk=None, *args, **kwargs):
        system = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = serializers.SystemDetailsSerializer(system, context=dict(request=request))
        return Response(serializer.data)


class Planets(viewsets.ReadOnlyModelViewSet):
    model = models.Planet
    serializer_class = serializers.PlanetSerializer
    queryset = models.Planet.objects.all()

    def retrieve(self, request, pk=None, *args, **kwargs):
        planet = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = serializers.PlanetDetailsSerializer(planet, context=dict(request=request))
        return Response(serializer.data)


class Buildings(viewsets.ReadOnlyModelViewSet):
    model = models.Building
    serializer_class = serializers.BuildingSerializer

    def get_queryset(self):
        if self.request.user.is_anonymous():
            return models.Building.objects.none()
        return self.request.user.buildings.all()

    @list_route()
    def Citadel(self, request):
        building = self.get_queryset().get(type='Citadel')
        return Response(self.serializer_class(building, context={'request': request}).data)

    @list_route()
    def Warehouse(self, request):
        building = self.get_queryset().get(type='Warehouse')
        return Response(self.serializer_class(building, context={'request': request}).data)


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

    @detail_route(methods=['post'])
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


#TODO move to another app
def section(request, name):
    return render(request, "section/%s.html" % name)


@api_view(('POST', ))
def next_turn(request):
    for building in request.user.buildings.all():
        building.process_turn()
    return Response()