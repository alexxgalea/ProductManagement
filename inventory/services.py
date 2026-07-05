from .models import Stock
from django.utils import timezone
from django.db.models import F
from django.db import transaction
from procurement.models import GoodsReceipt

@transaction.atomic
def apply_goods_receipt(gr_id):
    gr = GoodsReceipt.objects.select_for_update().get(pk=gr_id)
    if gr.applied:
        return
    for line in gr.lines.all():
        stock, _ = Stock.objects.get_or_create(location = gr.location,
                                               ingredient = line.ingredient,
                                               defaults={"quantity",0}
                                               )
        Stock.objects.filter(pk = stock.pk).update(quantity = F("quantity") + line.quantity)
    
    gr.applied = True
    gr.applied_at = timezone.now()
    gr.save()

