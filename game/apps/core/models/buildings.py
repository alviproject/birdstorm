import blinker
from concurrency.fields import IntegerVersionField
from django.db import models
from game.apps.core.models import components
from game.apps.core.models.planet.models import Planet
from game.apps.core.models.ships import Ship
from game.utils.models import ResourceContainer
from game.utils.polymorph import PolymorphicBase
from jsonfield import JSONField
import game.apps.core.signals


class Building(PolymorphicBase):
    level = models.IntegerField(default=1)
    data = JSONField()
    planet = models.ForeignKey(Planet, related_name="buildings")
    version = IntegerVersionField()

    class Meta:
        app_label = 'core'


class Provider(Building):
    def processes(self, *args, **kwargs):
        return self.data['processes']

    def order(self, order, quantity, ship, user, request_id):
        order_details = self.processes(ship)[order]

        messages = blinker.signal(game.apps.core.signals.messages % user.id)

        with ship.lock():
            for i in range(quantity):
                if quantity > 1:
                    message = "Producing %s, phase %d/%d, please wait" % (order, i+1, quantity)
                else:
                    message = "Producing %s, please wait" % order
                messages.send(self, message=dict(type="info", text=message,),)
                try:
                    for resource, qty in order_details['requirements'].items():
                        ship.remove_resource(resource, qty)
                except RuntimeError:
                    messages.send(self, message=dict(type="error", text="Not enough resources to fulfill this order",),)
                    return
                yield order_details['time']
                ship.save()
                self.fulfill_order(order, ship, user, order_details=order_details)
                messages.send(self, message=dict(type="success", text="Ordered item was added to your inventory",),)

    def fulfill_order(self, order, ship, user, order_details=None):
        raise NotImplementedError

    class Meta:
        app_label = 'core'
        proxy = True


class Plant(Provider):
    def fulfill_order(self, order, ship, user, order_details=None):
        ship.add_resource(order, 1)

    def processes(self, *args, **kwargs):
        return {name: self.PROCESSES[name] for name in self.data['processes']}

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


class Factory(Plant):
    PROCESSES = {
        "ShipStructures": {
            "time": 5,
            "requirements": {
                "Steel": 2,
                "Aluminium": 1,
            },
        },
        "ComponentStructures": {
            "time": 5,
            "requirements": {
                "Polymer": 1,
                "Aluminium": 1,
            },
        },
        "BuildingStructures": {
            "time": 5,
            "requirements": {
                "Steel": 4,
            },
        },
    }

    class Meta:
        proxy = True


class Mine(Building):
    class Meta:
        proxy = True


class Shipyard(Provider):
    def processes(self, _=None):
        #TODO this data shall be defined in ships module
        return {
            "Raven": {
                "time": 20,
                "requirements": {
                    "ShipStructures": 10,
                    "ComponentStructures": 10,
                },
            },
            "Owl": {
                "time": 25,
                "requirements": {
                    "ShipStructures": 20,
                    "ComponentStructures": 10,
                },
            },
            "Swallow": {
                "time": 20,
                "requirements": {
                    "ShipStructures": 15,
                    "ComponentStructures": 10,
                },
            },
        }

    def fulfill_order(self, order, ship, user, order_details=None):
        new_ship = Ship(type=order, owner=user, system=self.planet.system)
        new_ship.save()

    class Meta:
        proxy = True


class Warehouse(Building):
    class Container(ResourceContainer):
        def __init__(self, user):
            self.user = user

        @property
        def resources(self):
            return self.user.profile.data.setdefault('warehouse_resources', {})

    @staticmethod
    def get_resource_container(user):
        return Warehouse.Container(user)

    class Meta:
        proxy = True


class Smelter(Plant):
    PROCESSES = {
        "Steel": {
            "time": 5,
            "requirements": {
                "Coal": 1,
                "Iron": 1,
            },
        },
        "Aluminium": {
            "time": 10,
            "requirements": {
                "Bauxite": 2,
            },
        },
    }

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


class Refinery(Plant):
    PROCESSES = {
        "Polymer": {
            "time": 10,
            "requirements": {
                "Oil": 2
            }
        }
    }

    class Meta:
        proxy = True
