#TODO this could be a separate package
import django.db.models as models
from django.db.models.base import ModelBase


class PolymorphicMeta(ModelBase):
    """not to be used directly, inherit from PolymorphicBase instead"""
    def __call__(cls, *args, **kwargs):
        obj = super(PolymorphicMeta, cls).__call__(*args, **kwargs)
        obj.change_real_class()
        return obj


class PolymorphicBase(models.Model, metaclass=PolymorphicMeta):
    type = models.CharField(max_length=255)

    class Meta:
        abstract = True

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
        for cls in self.__class__.__subclasses__():
            if cls.__name__ == self.type:
                self.__class__ = cls
                return self
        raise RuntimeError("Subclass not found: %s %s", self.type, self.__class__.__name__)
