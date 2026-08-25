from django.contrib import admin

from inventory.services import apply_goods_receipt

from .models import GoodsReceipt, GoodsReceiptLine, Supplier

# Register your models here.
admin.site.register(Supplier)


class GoodsReceiptLineInline(admin.TabularInline):
    model = GoodsReceiptLine
    extra = 3
    show_change_link = True


@admin.action(description="Aplica pe stoc")
def apply_to_stock(modeladmin, request, queryset):
    for gr in queryset:
        apply_goods_receipt(gr.id)
    modeladmin.message_user(request, f"{queryset.count()} NIR-uri aplicate pe stoc.")


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = ["supplier", "location", "date", "document_number", "applied", "applied_at"]
    search_fields = ["document_number", "supplier__name"]
    readonly_fields = ["applied", "applied_at"]
    inlines = [GoodsReceiptLineInline]
    actions = [apply_to_stock]
