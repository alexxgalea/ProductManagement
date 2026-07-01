from django.contrib import admin
from .models import ReportedLoss
# Register your models here.

@admin.register(ReportedLoss)
class ReportedLossAdmin(admin.ModelAdmin):
    list_display = ["location","ingredient","quantity","reason","occurred_at","reported_by"]
    list_filter = ["location","reason","occurred_at"]
    search_fields = ["ingredient__name"]