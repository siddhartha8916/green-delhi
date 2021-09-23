from django.db import models

# Create your models here.
class air_quality(models.Model):
    date = models.DateField()
    aqi = models.IntegerField()
    pm25 = models.FloatField()
    pm10 = models.FloatField()



