# Generated by Django 3.0.2 on 2020-05-06 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventories', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='unit',
            field=models.CharField(choices=[('Mass', (('kilogram', 'kilogram'), ('gram', 'gram'))), ('Volume', (('liter', 'liter'), ('mililiter', 'mililiter')))], max_length=40),
        ),
    ]
