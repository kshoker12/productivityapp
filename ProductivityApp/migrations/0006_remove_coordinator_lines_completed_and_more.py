# Generated by Django 4.2.7 on 2023-11-15 21:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ProductivityApp', '0005_currentweek_selected'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coordinator',
            name='lines_completed',
        ),
        migrations.RemoveField(
            model_name='coordinator',
            name='orders_completed',
        ),
        migrations.RemoveField(
            model_name='coordinator',
            name='total_cost',
        ),
    ]