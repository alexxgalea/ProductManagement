import pytest
from .conftest import create_goods_receipt_line, create_stock, create_goods_receipt
from inventory.services import apply_goods_receipt, apply_reported_loss

@pytest.mark.django_db
def test_apply_goods_receipt(create_goods_receipt, create_goods_receipt_line, create_stock):
    good_receipt = create_goods_receipt
    stock = create_stock
    apply_goods_receipt(good_receipt.id)
    stock.refresh_from_db()
    assert stock.quantity == 30

@pytest.mark.django_db
def test_double_apply_does_not_double(create_goods_receipt, create_goods_receipt_line, create_stock):
    good_receipt = create_goods_receipt
    stock = create_stock
    apply_goods_receipt(good_receipt.id)
    stock.refresh_from_db()
    stock_quantity_first = stock.quantity
    assert stock_quantity_first == 30
    apply_goods_receipt(good_receipt.id)
    stock.refresh_from_db()
    stock_quantity_second = stock.quantity
    assert stock_quantity_first == stock_quantity_second

