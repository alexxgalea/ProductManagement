import factory
from accounts.models import User, Location, Membership, AuditLog


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Sequence(lambda n: f"Location {n}")
    address = factory.Faker("address")
