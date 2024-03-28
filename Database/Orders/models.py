from django.db import models
from Items.models import items
from Customers.models import customers


class orderItem(models.Model):
    quantity = models.IntegerField()
    item = models.ForeignKey(items, on_delete=models.CASCADE)
    order = models.ForeignKey('orders', on_delete=models.CASCADE)


class orders(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    customer = models.ForeignKey(customers, on_delete=models.CASCADE)
