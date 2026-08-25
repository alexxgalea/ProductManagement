from decimal import Decimal

import factory
from django.utils import timezone

from inventory.models import Stock, StockCount, StockCountLine


class StockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Stock

    location = factory.SubFactory("accounts.tests.factories.LocationFactory")
    ingredient = factory.SubFactory("core.tests.factories.IngredientFactory")
    quantity = Decimal("20.00")


class StockCountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StockCount

    location = factory.SubFactory("accounts.tests.factories.LocationFactory")
    date = factory.LazyFunction(timezone.now)


class StockCountLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StockCountLine

    stock_count = factory.SubFactory(StockCountFactory)
    ingredient = factory.SubFactory("core.tests.factories.IngredientFactory")
    counted_quantity = Decimal("18.00")
