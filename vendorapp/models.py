# models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count, Avg, F
from django.utils import timezone

class Vendor(models.Model):
    name = models.CharField(max_length=100)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=50, unique=True)
    on_time_delivery_rate = models.FloatField(default=0)
    quality_rating_avg = models.FloatField(default=0)
    average_response_time = models.FloatField(default=0)
    fulfillment_rate = models.FloatField(default=0)

    def __str___(self):
        return self.name


class PurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    )

    po_number = models.CharField(max_length=100, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='purchase_orders')
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    acknowledgment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.po_number


class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='historical_performance')
    date = models.DateField()
    on_time_delivery_rate = models.FloatField(default=0)
    quality_rating_avg = models.FloatField(default=0)
    average_response_time = models.FloatField(default=0)
    fulfillment_rate = models.FloatField(default=0)

    def __str__(self):
        return f'{self.fulfillment_rate} - {self.date}'


# Define a function to calculate and update performance metrics for a vendor
def update_vendor_performance_metrics(vendor):
    # Calculate On-Time Delivery Rate
    completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
    on_time_deliveries = completed_orders.filter(delivery_date__lte=F('order_date')).count()
    total_completed_orders = completed_orders.count()
    if total_completed_orders > 0:
        vendor.on_time_delivery_rate = on_time_deliveries / total_completed_orders * 100
    else:
        vendor.on_time_delivery_rate = 0

    # Calculate Quality Rating Average
    quality_avg = completed_orders.aggregate(avg_rating=Avg('quality_rating'))['avg_rating']
    vendor.quality_rating_avg = quality_avg if quality_avg is not None else 0

    # Calculate Average Response Time
    response_time_avg = completed_orders.aggregate(avg_response_time=Avg(F('acknowledgment_date') - F('issue_date')))['avg_response_time']
    vendor.average_response_time = response_time_avg.total_seconds() if response_time_avg is not None else 0

    # Calculate Fulfilment Rate
    total_orders = PurchaseOrder.objects.filter(vendor=vendor).count()
    fulfilled_orders = completed_orders.filter(issue_date=F('acknowledgment_date')).count()
    if total_orders > 0:
        vendor.fulfillment_rate = fulfilled_orders / total_orders * 100
    else:
        vendor.fulfillment_rate = 0

    vendor.save()



