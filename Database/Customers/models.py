from django.db import models


class customers(models.Model):
    name = models.CharField()
    billing_address = models.CharField()
    shipping_address = models.CharField()
    phone = models.CharField()
    email = models.CharField()
