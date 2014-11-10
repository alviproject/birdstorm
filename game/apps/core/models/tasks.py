import blinker
from concurrency.fields import IntegerVersionField
from django.contrib.auth.models import User, AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, validate_email, RegexValidator
from django.db import models
from django.db.models.signals import post_save
from game.apps.core.models.buildings import Building, Smelter
from game.utils.polymorph import PolymorphicBase
import game.apps.core.signals


class Task(PolymorphicBase):
    user = models.ForeignKey(User)
    state = models.CharField(max_length=256, default="started")
    archived = models.BooleanField(default=False)
    version = IntegerVersionField()

    def __str__(self):
        return "User: %s, task: %s, state: %s" % (self.user, self.type, self.state)

    def connect(self):
        if not self.signal_name():
            return

        def receiver(*args, **kwargs):
            task = Task.objects.get(id=self.id)
            task.receive_signal(*args, **kwargs)

        return blinker.signal(self.signal_name()).connect(receiver)

    def signal_name(self):
        pass

    def details(self):
        return {}

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        signal = blinker.signal(game.apps.core.signals.task_updated % self.user_id)
        signal.send(None, task_id=self.id, archived=self.archived, state=self.state, type=self.type)

    class Meta:
        ordering = ('-id',)


class Panels(Task):
    mission = "LearnTheInterface"

    def action(self, data):
        _type = data["type"]
        if self.state == "started" and _type == 'acknowledge':
            self.state = "click_any_system"
        elif self.state == "click_any_system" and _type == 'planet':
            self.state = "planet_not_star"
        elif self.state == "click_any_system" and _type == 'star':
            self.state = "star_system"
        elif self.state == "star_system" and _type == 'acknowledge':
            self.state = "left_panels"
        elif self.state == "planet_not_star" and _type == 'acknowledge':
            self.state = "left_panels"
        elif self.state == "left_panels" and _type == 'acknowledge':
            self.state = "close_details"
        elif self.state == "close_details" and _type == 'acknowledge':
            self.state = "map"
        elif self.state == "map" and _type == 'acknowledge':
            self.state = "summary"
        elif self.state == "summary" and _type == 'acknowledge':
            self.state = "finished"
            self.archived = True
            WhoIAm.objects.create(user=self.user)
            FirstScan.objects.create(user=self.user)
        else:
            raise ValidationError("Wrong state or type: %s, %s" % (self.state, _type))
        self.save()

    class Meta:
        proxy = True


class WhoIAm(Task):
    mission = "BuildingTrust"

    def action(self, data):
        _type = data["type"]
        if self.state == "started" and _type == 'acknowledge':
            self.state = "database"
        elif self.state == "database" and _type == 'acknowledge':
            WhoAreYou.objects.create(user=self.user, state="contact")
            self.archived = True
            self.state = "finished"
        self.save()

    class Meta:
        proxy = True


class WhoAreYou(Task):
    mission = "BuildingTrust"

    def action(self, data):
        _type = data["type"]
        if self.state == "contact" and _type == 'email':
            email = data["email"].lower()
            validate_email(email)
            if User.objects.filter(email=email).exclude(id=self.user.id):
                raise ValidationError("Email is already used")
            self.user.email = email
            self.user.save()
            self.state = "username"
        elif self.state == "username" and _type == 'username':
            username = data["username"]
            if User.objects.filter(username__iexact=username).exclude(id=self.user.id):
                raise ValidationError("Username is already used")
            RegexValidator(r'^[\w.@+-]+$', 'Enter a valid username.', 'invalid')(username)
            self.user.username = username
            self.user.save()
            self.state = "password"
        elif self.state == "password" and _type == 'password':
            password = data["password"]
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long")
            self.user.set_password(password)
            self.user.save()
            self.state = "confirm"
        elif self.state == "confirm" and _type == 'change_username':
            self.state = "username"
        elif self.state == "confirm" and _type == 'change_email':
            self.state = "contact"
        elif self.state == "confirm" and _type == 'change_password':
            self.state = "password"
        elif self.state == "confirm" and _type == 'verify':
            password = data["password"]
            if not self.user.check_password(password):
                raise ValidationError("Incorrect password")
            self.state = "summary"
        elif self.state == "summary" and _type == 'acknowledge':
            self.archived = True
            self.state = "finished"
        else:
            raise ValidationError("Wrong state or type: %s, %s" % (self.state, _type))
        self.save()

    class Meta:
        proxy = True


class FirstScan(Task):
    mission = "UpgradeYourShip"

    def signal_name(self):
        return game.apps.core.signals.planet_scan % self.user_id

    def receive_signal(self, sender):
        self.state = "summary"
        self.save()

    def action(self, data):
        _type = data["type"]
        if self.state == "started" and _type == 'acknowledge':
            self.state = "scan"
        elif self.state == "summary" and _type == 'acknowledge':
            self.archived = True
            self.state = "finished"
            Extraction.objects.create(user=self.user)
        else:
            raise ValidationError("Wrong state or type: %s, %s" % (self.state, _type))
        self.save()

    class Meta:
        proxy = True


class Extraction(Task):
    #TODO all of Task subclasses should probably utilize state pattern
    # this seems like a good candidate for analysis
    mission = "UpgradeYourShip"

    def signal_name(self):
        return game.apps.core.signals.planet_extract % self.user_id

    def receive_signal(self, sender, ship):
        if self.state == "started":
            self.state = "some_more"
        elif self.state == "some_more":
            for resource, quantity in self.details()["resources"].items():
                if ship.resources.get(resource, 0) < quantity:
                    return
            self.state = "summary"
        self.save()

    def action(self, data):
        _type = data["type"]
        if self.state == "started" and _type == 'acknowledge':
            self.state = "scan"
        if self.state == "summary" and _type == 'acknowledge':
            self.archived = True
            self.state = "finished"
            Alloys.objects.create(user=self.user)
        else:
            raise ValidationError("Wrong state or type: %s, %s" % (self.state, _type))
        self.save()

    def details(self):
        return {
            "resources": {
                "Coal": 20,
                "Iron": 20,
            }
        }

    class Meta:
        proxy = True


class Alloys(Task):
    mission = "UpgradeYourShip"

    def signal_name(self):
        return game.apps.core.signals.order % self.user_id

    def receive_signal(self, sender, ship):
        if self.state == "started":
            for resource, quantity in self.details()["resources"].items():
                if ship.resources.get(resource, 0) < quantity:
                    return
            self.state = "summary"
        self.save()

    def details(self):
        #TODO cache
        marked_buildings = [
            dict(
                planet_type=building.planet.type,
                planet_id=building.planet.id,
                system_id=building.planet.system_id,
                id=building.id,
            )
            for building in Building.objects.filter(type=Smelter.__name__)
        ]

        return {
            "resources": {
                "Steel": 10,
                "Aluminium": 10,
            },
            "marked_buildings": marked_buildings
        }

    class Meta:
        proxy = True


def create_task(sender, instance, created, *args, **kwargs):
    if created:
        Panels.objects.create(user=instance)


post_save.connect(create_task, sender=User, dispatch_uid="create_task")