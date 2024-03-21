from django.db import models


class customers(models.Model):
    name = models.CharField(max_length=0)
    billing_address = models.CharField(max_length=0)
    shipping_address = models.CharField(max_length=0)
    phone = models.CharField(max_length=0)
    email = models.CharField(max_length=0)
