from django.db import models


class manufacture(models.Model):
    quantity = models.IntegerField(max_length=0)
    date = models.DateTimeField(max_length=0)


class manufactureHistory(models.Model):
    pass
