import pytest
from .conftest import create_goods_receipt_line, create_stock, create_goods_receipt, create_reported_loss, create_stock_count, create_stock_count_line
from inventory.services import apply_goods_receipt, apply_reported_loss, apply_stock_count
import threading
from django.db import connections

@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("times",[1,2])
def test_repeated_apply_goods_receipt_same_effect(create_goods_receipt, create_goods_receipt_line, create_stock, times):
    for _ in range(times):
        apply_goods_receipt(create_goods_receipt.id)
    create_stock.refresh_from_db()
    assert create_stock.quantity == 30

@pytest.mark.django_db(transaction=True)
def test_two_workers_racing_do_not_double_apply(create_goods_receipt, create_goods_receipt_line, create_stock):
    good_receipt_id = create_goods_receipt.id

    barrier = threading.Barrier(2)

    def worker():
        barrier.wait()
        try:
            apply_goods_receipt(good_receipt_id)
        finally:
            connections.close_all()

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    create_stock.refresh_from_db()
    assert create_stock.quantity == 30


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("times",[1,2])
def test_repeated_apply_reported_loss_same_effect(create_stock, create_reported_loss, times):
    for _ in range(times):
        apply_reported_loss(create_reported_loss.id)
    create_stock.refresh_from_db()
    assert create_stock.quantity == 15

@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("times",[1,2])
def test_repeated_apply_stock_count_same_effect(create_stock ,create_stock_count, create_stock_count_line, times):
    for _ in range(times):
        apply_stock_count(create_stock_count.id)
    create_stock.refresh_from_db()
    assert create_stock.quantity == 18  


