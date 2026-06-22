from django.contrib import admin
from .models import Membership, User, Location, AuditLog

# Register your models here.
admin.site.register(Membership)
admin.site.register(User)
admin.site.register(Location)
admin.site.register(AuditLog)