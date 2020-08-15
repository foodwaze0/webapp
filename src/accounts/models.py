from django.db import models

# Create your models here.
class Restriction(models.Model):
	username		= models.CharField(max_length=40)
	ingr 			= models.CharField(max_length=50)
	check			= models.BooleanField(default=True)