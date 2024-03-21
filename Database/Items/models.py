from django.db import models


class items(models.Model):
    name = models.CharField()
    description = models.CharField()
    price = models.CharField()
    target_inv = models.IntegerField()
    current_inv = models.IntegerField()
    reorder_level = models.IntegerField()
