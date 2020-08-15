from django import forms

from .models import Inventory

class InventoryModelForm(forms.ModelForm):

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
				('bc', 'Bunch'),
				('cn', 'Can'),
				('cv', 'Clove'),
				('h', 'Head'),
				('p', 'Pack'),
				('pg', 'Package'),
				('pc', 'Piece'),
				('po', 'Pouch'),
				('s', 'Stalk'),
				('w', 'Whole'),
			)
		),
	]

	ingr		= forms.CharField(
					        widget=forms.TextInput(
					        	attrs={
					        		'class': 'form-control',
					        		'name': 'ingredient',
					        		'list': 'ingrList',
					        		'autocomplete': 'off',
					        	}
					        )
						)

	qty			= forms.CharField(
					        widget=forms.TextInput(
					        	attrs={
					        		'class': 'form-control',
					        		'name': 'quantity',
					        		'autocomplete': 'off',
					        	}
					        )
						)

	unit		= forms.ChoiceField(
							choices=UNIT_CHOICES,
					        widget=forms.Select(
					        	attrs={
					        		'class': 'form-control',
					        		'name': 'unit',
					        	}
					        )
						)

	class Meta:
		model = Inventory
		fields = [
			'ingr',
			'qty',
			'unit',
			'check',
		]
	
	# validation below

class AddInventoryForm(forms.ModelForm):

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
				('bc', 'Bunch'),
				('cn', 'Can'),
				('cv', 'Clove'),
				('h', 'Head'),
				('p', 'Pack'),
				('pg', 'Package'),
				('pc', 'Piece'),
				('po', 'Pouch'),
				('s', 'Stalk'),
				('w', 'Whole'),
			)
		),
	]


	ingr		= forms.CharField(
					        widget=forms.TextInput(
					        	attrs={
					        		'class': 'form-control',
					        		'name': 'ingredient',
					        		'list': 'ingrList',
					        		'autocomplete': 'off',
					        	}
					        )
						)

	qty			= forms.CharField(
					        widget=forms.TextInput(
					        	attrs={
					        		'class': 'form-control',
					        		'name': 'quantity',
					        		'autocomplete': 'off',
					        	}
					        )
						)

	unit		= forms.ChoiceField(
							choices=UNIT_CHOICES,
					        widget=forms.Select(
					        	attrs={
					        		'class': 'form-control',
					        		'name': 'unit',
					        	}
					        )
						)

	class Meta:
		model = Inventory
		fields = [
			'ingr',
			'qty',
			'unit',
			'check',
		]
	
	# validation below

	# def clean_ingr(self, *args, **kwargs):
	# 	ingr = str(self.cleaned_data['ingr'])
	# 	username = 
	# 	check = Inventory.objects.filter(username=username).filter(ingr__iexact=ingr).count()
	# 	if check >= 1:
	# 		raise forms.ValidationError("Already Exist on Inventor")

	# 	return ingr




