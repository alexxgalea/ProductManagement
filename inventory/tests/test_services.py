import pytest
from .conftest import create_goods_receipt_line, create_stock, create_goods_receipt, create_reported_loss, create_stock_count, create_stock_count_line
from inventory.services import apply_goods_receipt, apply_reported_loss, apply_stock_count

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

@pytest.mark.django_db
def test_apply_reported_loss(create_stock, create_reported_loss):
    stock = create_stock
    reported_loss = create_reported_loss

    apply_reported_loss(reported_loss.id)
    stock.refresh_from_db()
    assert stock.quantity == 15

@pytest.mark.django_db
def test_double_loss_does_not_double(create_stock, create_reported_loss):
    stock = create_stock
    reported_loss = create_reported_loss

    apply_reported_loss(reported_loss.id)
    stock.refresh_from_db()
    assert stock.quantity == 15
    stock_quantity_first = stock.quantity
    apply_reported_loss(reported_loss.id)
    stock.refresh_from_db()
    stock_quantity_second = stock.quantity
    assert stock_quantity_first == stock_quantity_second

@pytest.mark.django_db
def test_apply_stock_count(create_stock ,create_stock_count, create_stock_count_line):
    stock = create_stock
    stock_count = create_stock_count
    apply_stock_count(stock_count.id)
    stock.refresh_from_db()
    assert stock.quantity == 18

@pytest.mark.django_db
def test_double_stock_count_does_not_double(create_stock ,create_stock_count, create_stock_count_line):
    stock = create_stock
    stock_count = create_stock_count
    
    apply_stock_count(stock_count.id)
    stock.refresh_from_db()
    assert stock.quantity == 18
    apply_stock_count(stock_count.id)
    stock.refresh_from_db()
    assert stock.quantity == 18

