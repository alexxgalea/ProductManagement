from django.contrib import admin
from .models import GoodsReceipt, GoodsReceiptLine, Supplier

# Register your models here.
admin.site.register(Supplier)


class GoodsReceiptLineInline(admin.TabularInline):
    model = GoodsReceiptLine
    extra = 3
    show_change_link = True

@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = ["supplier","location","date","document_number"]
    search_fields = ["document_number", "supplier__name"]

    inlines = [GoodsReceiptLineInline]


