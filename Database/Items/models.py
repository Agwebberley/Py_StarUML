from django.db import models


class items(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    price = models.CharField()
    target_inv = models.IntegerField()
    current_inv = models.IntegerField()
    reorder_level = models.IntegerField()
