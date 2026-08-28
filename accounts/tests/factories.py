import factory

from accounts.models import Location, Membership, User


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Sequence(lambda n: f"Location {n}")
    address = factory.Faker("address")


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        raw_password = extracted or "pw12345"
        self.set_password(raw_password)
        if create:
            self.save()


class MembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Membership

    user = factory.SubFactory(UserFactory)
    location = factory.SubFactory(LocationFactory)
    role = Membership.Role.worker
