from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(HistoricalPerformance)
admin.site.register(PurchaseOrder)
admin.site.register(Vendor)