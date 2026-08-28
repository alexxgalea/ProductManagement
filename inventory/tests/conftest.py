from decimal import Decimal

import pytest

from accounts.tests.factories import LocationFactory
from core.tests.factories import IngredientFactory
from inventory.tests.factories import StockCountFactory, StockCountLineFactory, StockFactory
from losses.models import ReportedLoss
from losses.tests.factories import LossFactory
from procurement.tests.factories import (
    GoodsReceiptFactory,
    GoodsReceiptLineFactory,
    SupplierFactory,
)


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
def create_stock_count(create_location):
    return StockCountFactory.create(location=create_location)


@pytest.fixture
def create_stock_count_line(create_stock_count, create_ingredient):
    return StockCountLineFactory.create(
        stock_count=create_stock_count, ingredient=create_ingredient
    )


@pytest.fixture
def create_goods_receipt(create_supplier, create_location):
    return GoodsReceiptFactory.create(supplier=create_supplier, location=create_location)


@pytest.fixture
def create_goods_receipt_line(create_goods_receipt, create_ingredient):
    return GoodsReceiptLineFactory.create(
        goods_receipt=create_goods_receipt, ingredient=create_ingredient
    )


@pytest.fixture
def create_reported_loss(create_stock):
    stock = create_stock
    return LossFactory.create(
        location=stock.location,
        ingredient=stock.ingredient,
        quantity=Decimal("5.00"),
        reason=ReportedLoss.Reason.ROTTEN,
    )
