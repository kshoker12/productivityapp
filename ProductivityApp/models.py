from django.db import models

class Coordinator(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(null = False, max_length = 50)
    orders_completed = models.IntegerField(default = 0)
    lines_completed = models.IntegerField(default = 0)
    total_cost = models.DecimalField(default = 0, max_digits = 10, decimal_places = 2)

    def __str__(self):
        return "Name: " + self.name 
