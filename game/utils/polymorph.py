#TODO this could be a separate package
import django.db.models as models
from django.db.models.base import ModelBase


class PolymorphicMeta(ModelBase):
    """not to be used directly, inherit from PolymorphicBase instead"""
    def __call__(cls, *args, **kwargs):
        obj = super(PolymorphicMeta, cls).__call__(*args, **kwargs)
        obj.change_real_class()  # TODO call to __init__ of real class is omitted
        return obj


class PolymorphicBase(models.Model, metaclass=PolymorphicMeta):
    type = models.CharField(max_length=255, help_text=None)

    class Meta:
        abstract = True

    @classmethod
    def subclasses(cls):
        return cls.__subclasses__() + [g for s in cls.__subclasses__() for g in s.subclasses()]

    def change_real_class(self):
        """changes class of an object basing on "type" field"""
        if not self.type:
            #objects was just created, set type and return
            self.type = self.__class__.__name__
            return self
        if self.type == self.__class__.__name__:
            return self
        #type is set, we can do actual change of the class
        #TODO it could be cached during creation of relevant subclasses
        for cls in self.subclasses():
            if cls.__name__ == self.type:
                self.__class__ = cls
                return self
        raise RuntimeError("Subclass not found: %s %s", self.type, self.__class__.__name__)
