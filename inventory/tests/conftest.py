import pytest
from inventory.tests.factories import StockFactory
from core.tests.factories import IngredientFactory
from accounts.tests.factories import LocationFactory
from procurement.tests.factories import SupplierFactory, GoodsReceiptFactory, GoodsReceiptLineFactory

@pytest.fixture
def create_location():
    return LocationFactory.create()
@pytest.fixture
def create_ingredient():
    return IngredientFactory.create()

            
@pytest.fixture
def create_supplier():
    return SupplierFactory.create()

@pytest.fixture
def create_stock(create_location, create_ingredient):
    return StockFactory.create(location=create_location, ingredient=create_ingredient)

@pytest.fixture
def create_goods_receipt(create_supplier, create_location):
    return GoodsReceiptFactory.create(supplier=create_supplier, location=create_location)

@pytest.fixture
def create_goods_receipt_line(create_goods_receipt, create_ingredient):
    return GoodsReceiptLineFactory.create(goods_receipt=create_goods_receipt, ingredient=create_ingredient)