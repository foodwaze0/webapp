from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import Restriction

class CreateUserForm(UserCreationForm):
	username		= forms.CharField(
					        widget=forms.TextInput(
					        	attrs={
					        		'class': 'form-control',
					        		'name': 'username',
					        		'placeholder': 'Username',
					        	}
					        )
						)
	email 			= forms.CharField(
					        widget=forms.EmailInput(
					        	attrs={
					        		'class': 'form-control',
					        		'name': 'email',
					        		'placeholder': 'Email',
					        	}
					        )
				        )
	password1		= forms.CharField(
					        widget=forms.PasswordInput(
					        	attrs={
					        		'class': 'form-control',
					        		'name': 'password1',
					        		'placeholder': 'Password',
					        	}
					        )
				        )
	password2		= forms.CharField(
					        widget=forms.PasswordInput(
					        	attrs={
					        		'class': 'form-control',
					        		'name': 'password2',
					        		'placeholder': 'Re-enter Password',
					        	}
					        )
				        )


	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']

class AddRestrictionForm(forms.ModelForm):

	ingr 		= forms.CharField(
					        widget=forms.TextInput(
					        	attrs={
					        		'class': 'form-control',
					        		'name': 'ingr',
					        		'placeholder': 'Ingredient Name',
					        	}
					        )
						)

	class Meta:
		model = Restriction
		fields = ['ingr']

