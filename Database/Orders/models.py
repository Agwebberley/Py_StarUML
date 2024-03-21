from django.db import models


class orders(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    customer = models.ForeignKey('Customers.customers', on_delete=models.CASCADE)


class orderItem(models.Model):
    quantity = models.IntegerField()
