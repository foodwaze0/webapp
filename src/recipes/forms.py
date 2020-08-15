from django import forms

from .models import Rating

class RatingModelForm(forms.ModelForm):
	class Meta:
		review		= forms.CharField(
					        widget=forms.Textarea(
					        	attrs={
					        		'class': 'form-control',
					        		'name': 'review',
					        		'placeholder': 'Write Your Review Here',
					        	}
					        )
						)

		model = Rating
		fields = [
			'review',
		]