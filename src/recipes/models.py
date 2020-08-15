from django.db import models
from django.urls import reverse
from django.utils import timezone

# Create your models here.

class Recipe(models.Model):
	Recipe			= models.CharField(max_length=150)
	Title_link		= models.SlugField(null=True, unique=True)
	Thumbnail		= models.TextField(null=True)
	Servings		= models.CharField(null=True, max_length=20)
	Ingredients		= models.TextField(null=True)
	Instructions	= models.TextField(null=True)
	tag 			= models.TextField(null=True)
	cook 			= models.BigIntegerField(null=True)
	recipes_view	= models.BigIntegerField(null=True)

	def get_absolute_url(self):
		return reverse("recipes:recipe-detail", kwargs={"Title_link": self.Title_link})


class Rating(models.Model):
	# recipe_id		= models.BigIntegerField()
	recipe			= models.ForeignKey(Recipe, on_delete=models.CASCADE)
	user_id			= models.BigIntegerField(null=True)
	rating 			= models.CharField(max_length=1, null=True)
	orating			= models.CharField(max_length=1, null=True)
	review 			= models.TextField(null=True)
	posted_at		= models.DateTimeField(default=timezone.now)



class Ingredient(models.Model):
	recipe_id		= models.BigIntegerField()
	name 			= models.TextField(null=True)
	qty				= models.TextField(null=True)
	unit 			= models.TextField(null=True)
	ext 			= models.TextField(null=True)


class Matrix(models.Model):
	user_id = models.BigIntegerField()
	rating_list = models.TextField(null=True)