from decimal import Decimal

import factory
from inventory.models import Stock

class StockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Stock
        
    location = factory.SubFactory("accounts.tests.factories.LocationFactory")
    ingredient = factory.SubFactory("core.tests.factories.IngredientFactory")
    quantity = Decimal('20.00')