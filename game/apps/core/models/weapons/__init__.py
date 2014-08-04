import abc


class Weapon(abc.ABC):
    _properties = dict()

    @classmethod
    def range(cls):
        return cls._properties['range']

    @classmethod
    def frequency(cls):
        return cls._properties['frequency']

    @classmethod
    def damage(cls):
        return cls._properties['damage']


class ParticleBeam(Weapon):
    pass


class IonBeam(ParticleBeam):
    pass


class ElectronBeam(IonBeam):
    _properties = dict(
        range=10,
        frequency=4,
        damage=10,
    )


class NeutralParticleBeam(ParticleBeam):
    pass


class KineticGun(Weapon):
    pass


class RailGun(Weapon):
    pass


class GaussCannon(Weapon):
    pass