# Generated by Django 3.0.2 on 2020-01-25 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=40)),
                ('ingr', models.CharField(max_length=100)),
                ('qty', models.CharField(max_length=100)),
                ('unit', models.CharField(max_length=40)),
                ('check', models.BooleanField(default=False)),
            ],
        ),
    ]
