from django.db import models
from django.urls import reverse

# Create your models here.

class Inventory(models.Model):

	UNIT_CHOICES = [
		('nothing', '---Select a Unit---'
		),
		('Mass', (
				('g', 'Gram'),
				('kg', 'Kilogram'),
				('oz', 'Ounce'),
				('lb', 'Pound'),
			)
		),
		('Volume', (
				('c', 'Cup'),
				('foz', 'Fluid Ounce'),
				('l', 'Liter'),
				('ml', 'Mililiter'),
				('qt', 'Quart'),
				('tbsp', 'Tablespoon'),
				('tsp', 'Teaspoon'),
			)
		),
		('Others',(
				('bb', 'Big Bottle'),
				('b', 'Bottle'),
				('cn', 'Can'),
				('cv', 'Clove'),
				('h', 'Head'),
				('p', 'Pack'),
				('pc', 'Piece'),
				('po', 'Pouch'),
				('s', 'Stalk'),
				('w', 'Whole'),
			)
		),
	]

	username		= models.CharField(max_length=40)
	ingr			= models.CharField(max_length=100)
	qty				= models.CharField(max_length=100)
	unit 			= models.CharField(max_length=40, choices=UNIT_CHOICES)
	check 			= models.BooleanField(default=False)

	def get_absolute_url(self):
		return reverse("inventories:inventory-detail", kwargs={"id": self.id})
