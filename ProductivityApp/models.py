from django.db import models

class Coordinator(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(null = False, max_length = 50)

    def __str__(self):
        return "Name: " + self.name 

class Week(models.Model):
    coordinator = models.ForeignKey(Coordinator, on_delete=models.CASCADE, related_name='week')
    week = models.IntegerField(null = False)
    orders_completed = models.IntegerField(default = 0)
    lines_completed = models.IntegerField(default = 0)
    total_cost = models.DecimalField(default = 0, max_digits = 10, decimal_places = 2)


class CurrentWeek(models.Model):
    week = models.IntegerField(null = False)
    name = models.CharField(max_length = 50)
    selected = models.BooleanField(default = False)

class Files(models.Model):
    name = models.CharField(max_length = 50)

class AppState(models.Model):
    update = models.BooleanField(default = False)