from django.db import models


class customers(models.Model):
    name = models.CharField(max_length=255)
    billing_address = models.CharField(max_length=255)
    shipping_address = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
