from decimal import Decimal

import factory

from losses.models import ReportedLoss


class LossFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "losses.ReportedLoss"

    location = factory.SubFactory("accounts.tests.factories.LocationFactory")
    ingredient = factory.SubFactory("core.tests.factories.IngredientFactory")
    quantity = Decimal("5.00")
    reason = ReportedLoss.Reason.ROTTEN
