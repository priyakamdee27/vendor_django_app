from datetime import timezone
from datetime import datetime
from django.shortcuts import render
from django.dispatch import receiver  
from rest_framework import generics
from django.db.models.signals import post_save 

from .models import Vendor, PurchaseOrder, update_vendor_performance_metrics,HistoricalPerformance
from .serializers import VendorSerializer, PurchaseOrderSerializer


class VendorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer


class VendorRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True  # Allow partial updates
        return super().update(request, *args, **kwargs)


class PurchaseOrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer


class PurchaseOrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

# Signal to update vendor performance metrics after each PurchaseOrder save
@receiver(post_save, sender=PurchaseOrder)
def update_vendor_metrics(sender, instance, created, **kwargs):
    if instance.vendor:
        update_vendor_performance_metrics(instance.vendor)

# Signal to update historical performance metrics
@receiver(post_save, sender=Vendor)
def update_historical_performance(sender, instance, created, **kwargs):
    if created:
        HistoricalPerformance.objects.create(
            vendor=instance,
            date=datetime.now(timezone.utc).date(),
            on_time_delivery_rate=instance.on_time_delivery_rate,
            quality_rating_avg=instance.quality_rating_avg,
            average_response_time=instance.average_response_time,
            fulfillment_rate=instance.fulfillment_rate
        )