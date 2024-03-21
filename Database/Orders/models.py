from django.db import models
from Customers.models import customers


class orders(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    customer = models.ForeignKey(customers, on_delete=models.CASCADE)


class orderItem(models.Model):
    quantity = models.IntegerField()
    order = models.ForeignKey('orders', on_delete=models.CASCADE)
