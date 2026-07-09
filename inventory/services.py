from .models import Stock
from django.utils import timezone
from django.db.models import F
from django.db import transaction
from procurement.models import GoodsReceipt
from losses.models import ReportedLoss
from inventory.models import StockCount, Stock, StockCountLine


@transaction.atomic
def apply_goods_receipt(gr_id):
    gr = GoodsReceipt.objects.select_for_update().get(pk=gr_id)
    if gr.applied:
        return
    for line in gr.lines.all():
        stock, _ = Stock.objects.get_or_create(
            location=gr.location, ingredient=line.ingredient, defaults={"quantity": 0}
        )
        Stock.objects.filter(pk=stock.pk).update(quantity=F("quantity") + line.quantity)

    gr.applied = True
    gr.applied_at = timezone.now()
    gr.save()


@transaction.atomic
def apply_reported_loss(loss_id):
    loss = ReportedLoss.objects.select_for_update().get(pk=loss_id)
    if loss.applied:
        return
    stock, _ = Stock.objects.get_or_create(
        location=loss.location, ingredient=loss.ingredient, defaults={"quantity": 0}
    )
    Stock.objects.filter(pk=stock.pk).update(quantity=F("quantity") - loss.quantity)

    loss.applied = True
    loss.applied_at = timezone.now()
    loss.save()

@transaction.atomic
def apply_stock_count(sc_id):
    sc = StockCount.objects.select_for_update().get(pk = sc_id)
    if sc.applied:
        return
    for line in sc.stock_lines.all():
        stock, _ = Stock.objects.get_or_create(
            location = sc.location,
            ingredient = line.ingredient,
            defaults={"quantity": 0}
        )
        Stock.objects.filter(pk = stock.pk).update(quantity = line.counted_quantity)

    sc.applied = True
    sc.applied_at = timezone.now()
    sc.save()
    
