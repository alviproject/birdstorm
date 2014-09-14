import abc
import blinker
from django.db import models
from game.apps.core.models import components
from game.apps.core.models.components.drills import Drill
from game.apps.core.models.components.engines import Engine
from game.apps.core.models.components.scanners import Scanner
from game.apps.core.models.planet.models import Planet
from game.apps.core.models.ships import Ship
from game.utils.models import ResourceContainer
from game.utils.polymorph import PolymorphicBase
from jsonfield import JSONField
from rest_framework import serializers
import game.apps.core.signals


class Building(PolymorphicBase):
    level = models.IntegerField(default=1)
    data = JSONField()
    planet = models.ForeignKey(Planet, related_name="buildings")

    class Meta:
        app_label = 'core'


class Provider(Building):
    def processes(self, *args, **kwargs):
        return self.data['processes']

    def order(self, order, quantity, ship, user, request_id):
        order_details = self.processes(ship)[order]

        signal_id = "%d_%s" % (self.planet_id, request_id)
        actions_signal = blinker.signal(game.apps.core.signals.planet_actions_progress % signal_id)

        with ship.lock():
            for i in range(quantity):
                if quantity > 1:
                    message = "Producing %s, phase %d/%d, please wait" % (order, i+1, quantity)
                else:
                    message = "Producing %s, please wait" % order
                actions_signal.send(self, message=dict(type="info", text=message,),)
                try:
                    for resource, qty in order_details['requirements'].items():
                        ship.remove_resource(resource, qty)
                except RuntimeError:
                    actions_signal.send(self, message=dict(type="error", text="Not enough resources to fulfill this order",),)
                    return
                yield order_details['time']
                ship.save()
                self.fulfill_order(order, ship, user, order_details=order_details)
                actions_signal.send(self, message=dict(type="success", text="Ordered item was added to your inventory",),)

    def fulfill_order(self, order, ship, user, order_details=None):
        raise NotImplementedError

    class Meta:
        app_label = 'core'
        proxy = True


class Plant(Provider):
    def fulfill_order(self, order, ship, user, order_details=None):
        ship.add_resource(order, 1)

    class Meta:
        app_label = 'core'
        proxy = True


class Port(Building, ResourceContainer):
    OFFER_FACTOR = 1.5

    @property
    def prices(self):
        base_prices = self.data.get('prices') or {}
        result = dict()
        for type, price in base_prices.items():
            result[type] = dict(
                sale_price=int(price*Port.OFFER_FACTOR),
                purchase_price=int(price/Port.OFFER_FACTOR),
                available=self.resources.get(type, 0),
            )
        return result

    class Meta:
        proxy = True


class Factory(Building):
    class Meta:
        proxy = True


class Mine(Building):
    class Meta:
        proxy = True


class Shipyard(Building):
    @staticmethod
    def available_ships():
        return dict(
            Raven=dict(
                requirements=dict(
                    Coal=5,
                    Iron=3,
                ),
                time=5,
            ),
            Owl=dict(
                resources=dict(
                    Coal=15,
                    Iron=10,
                ),
                time=10,
            ),
            Swallow=dict(
                resources=dict(
                    Coal=20,
                    Iron=20,
                ),
                time=15,
            ),
        )

    def fulfill_order(self, order, ship, user, order_details=None):
        new_ship = Ship(type=order, owner=user, system=self.planet.system)
        new_ship.save()

    class Meta:
        proxy = True


class Warehouse(Building):
    class Meta:
        proxy = True


class Smelter(Plant):
    class Meta:
        proxy = True


class Workshop(Provider):
    def processes(self, ship=None):
        result = {}
        for name, details in self.data['processes'].items():
            component_kind = components.create_kind(details['component'])
            parameters = {"type": name}
            if ship and ship.get_component(details['component']).type == name:
                mark = ship.get_component(details['component']).mark + 1
                if mark > details['max_level']:
                    continue
                parameters["mark"] = mark
            result[name] = component_kind.create(parameters).process()
        return result

    def fulfill_order(self, order, ship, user, order_details=None):
        component_kind = order_details['kind']
        current_component = ship.get_component(component_kind)
        if current_component.type == order:
            current_component.mark += 1
            ship.set_component(current_component)
        else:
            component = components.create_kind(component_kind).create({type: order})
            ship.add_item(component)
        ship.save()

    class Meta:
        proxy = True


class Refinery(Building):
    class Meta:
        proxy = True


class BuildingBaseSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Building
        exclude = ['data']


class PortSerializer(BuildingBaseSerializer):
    prices = serializers.Field(source='prices')


class ProviderSerializer(BuildingBaseSerializer):
    processes = serializers.Field(source='processes')


#class WorkshopSerializer(BuildingBaseSerializer):
#    processes = serializers.SerializerMethodField('get_processes')
#
#    def get_processes(self, obj):
#        user = self.context['request'].user
#        if not user.is_authenticated():
#            return {}
#        return user.profile.warehouse_resources(obj.id)


class WarehouseSerializer(BuildingBaseSerializer):
    resources = serializers.SerializerMethodField('get_resources')

    def get_resources(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated():
            return {}
        return user.profile.warehouse_resources(obj.id)


class BuildingSerializer(serializers.HyperlinkedModelSerializer):
    def to_native(self, obj):
        #TODO use isinstance
        if obj.type == "Port":
            return PortSerializer(obj, context=self.context).to_native(obj)
        if isinstance(obj, Provider):
            return ProviderSerializer(obj, context=self.context).to_native(obj)
        if obj.type == "Warehouse":
            return WarehouseSerializer(obj, context=self.context).to_native(obj)
        return super().to_native(obj)

    class Meta(BuildingBaseSerializer.Meta):
        pass
