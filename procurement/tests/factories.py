from decimal import Decimal

import factory
from django.utils import timezone

from procurement.models import GoodsReceipt, GoodsReceiptLine, Supplier


class SupplierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Supplier

    name = factory.Sequence(lambda n: f"Supplier {n}")
    cif = factory.Sequence(lambda n: f"CIF{n}")


class GoodsReceiptFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GoodsReceipt

    supplier = factory.SubFactory(SupplierFactory)
    location = factory.SubFactory("accounts.tests.factories.LocationFactory")
    date = factory.LazyFunction(timezone.now)
    document_number = factory.Sequence(lambda n: f"GR{n}")


class GoodsReceiptLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GoodsReceiptLine

    goods_receipt = factory.SubFactory(GoodsReceiptFactory)
    ingredient = factory.SubFactory("core.tests.factories.IngredientFactory")
    quantity = Decimal("10.00")
    unit_price = Decimal("30.00")
