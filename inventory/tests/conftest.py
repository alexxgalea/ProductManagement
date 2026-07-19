import pytest
from core.models import Ingredient
from accounts.models import Location
from procurement.models import Supplier
from inventory.models import Stock
from decimal import Decimal
from django.utils import timezone


from procurement.models import GoodsReceipt, GoodsReceiptLine


@pytest.fixture
def create_location():
    return Location.objects.create(name="Test",
                                   address="")
@pytest.fixture
def create_ingredient():
    return Ingredient.objects.create(name="Carne",
                                     unit="kg",
                                     ingredient_type=Ingredient.IngredientType.INGREDIENT)

@pytest.fixture
def create_supplier():
    return Supplier.objects.create(name="Furnizor test")

@pytest.fixture
def create_stock(create_location, create_ingredient):
    return Stock.objects.create(location=create_location,
                                ingredient=create_ingredient,
                                quantity=Decimal("20"))

@pytest.fixture
def create_goods_receipt(create_supplier, create_location):
    return GoodsReceipt.objects.create(supplier=create_supplier,
                                       location=create_location,
                                       date=timezone.now(),
                                       document_number="TEST-1")

@pytest.fixture
def create_goods_receipt_line(create_goods_receipt, create_ingredient):
    return GoodsReceiptLine.objects.create(goods_receipt=create_goods_receipt,
                                           ingredient=create_ingredient,
                                           quantity=Decimal("10"),
                                           unit_price=Decimal("30"))