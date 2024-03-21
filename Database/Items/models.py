from django.db import models


class items(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=0)
    price = models.CharField(max_length=0)
    target_inv = models.IntegerField(max_length=0)
    current_inv = models.IntegerField(max_length=0)
    reorder_level = models.IntegerField(max_length=0)
