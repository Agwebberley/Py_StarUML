from django.db import models


class manufacture(models.Model):
    quantity = models.IntegerField()
    date = models.DateTimeField()


class manufactureHistory(models.Model):
    pass
