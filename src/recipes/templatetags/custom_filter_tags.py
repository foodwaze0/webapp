from django import template
from recipes.models import Recipe, Rating
from accounts.models import Restriction
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Sum, Q
from random import shuffle
from operator import attrgetter
#regular expression
import re

register = template.Library()

# to use simple_tag on template {% simple_tag_name variable %}
# to generate new variable with it {% simple_tag_name variable as new variable %} 

# jargon checker
@register.simple_tag(name='cjargon')
def cjargon(value):
	bags = ['al dente', 'bake', 'baste', 'batch cooking', 'beat', 'blanch', 'blend', 'boil', 'braise', 'bring to the boil', 'caramelise', 'char grill', 'chop', 'chop finely', 'chop roughly', 'cream', 'deglaze', 'dice', 'dredge', 'drizzle', 'dry fry', 'flambé', 'flambe', 'fold', 'fried', 'fry', 'glaze', 'grate', 'grill', 'knead', 'line', 'lightly oil', 'marinate', 'par-boil', 'peel', 'poach', 'pre-heat', 'pulse', 'purée', 'puree', 'reduce', 'refresh', 'reheat', 'roast', 'roll', 'rub in', 'sauté', 'saute', 'sear', 'sieve', 'simmer', 'slice', 'soak', 'steam', 'stew', 'sweat', 'whisk', 'zest']
	for bag in bags:
		txt = value
		x = re.search(""+bag+"", txt, re.IGNORECASE)
		if x != None:
			out = True
			break
		else:
			out = False

	return out

# extract words before the jargon
@register.simple_tag(name='words1')
def words1(value):
	bags = ['al dente', 'bake', 'baste', 'batch cooking', 'beat', 'blanch', 'blend', 'boil', 'braise', 'bring to the boil', 'caramelise', 'char grill', 'chop', 'chop finely', 'chop roughly', 'cream', 'deglaze', 'dice', 'dredge', 'drizzle', 'dry fry', 'flambé', 'flambe', 'fold', 'fried', 'fry', 'glaze', 'grate', 'grill', 'knead', 'line', 'lightly oil', 'marinate', 'par-boil', 'peel', 'poach', 'pre-heat', 'pulse', 'purée', 'puree', 'reduce', 'refresh', 'reheat', 'roast', 'roll', 'rub in', 'sauté', 'saute', 'sear', 'sieve', 'simmer', 'slice', 'soak', 'steam', 'stew', 'sweat', 'whisk', 'zest']
	txt = value
	out = ""
	for bag in bags:
		x = re.search(""+bag+"", txt, re.IGNORECASE)
		if x != None:
			temp = re.split("[\\w\\S]*"+bag+"[\\w\\S]*", txt, 1, re.IGNORECASE)
			out = temp[0]
			break

	return out

# extract words after the jargon
@register.simple_tag(name='words2')
def words2(value):
	bags = ['al dente', 'bake', 'baste', 'batch cooking', 'beat', 'blanch', 'blend', 'boil', 'braise', 'bring to the boil', 'caramelise', 'char grill', 'chop', 'chop finely', 'chop roughly', 'cream', 'deglaze', 'dice', 'dredge', 'drizzle', 'dry fry', 'flambé', 'flambe', 'fold', 'fried', 'fry', 'glaze', 'grate', 'grill', 'knead', 'line', 'lightly oil', 'marinate', 'par-boil', 'peel', 'poach', 'pre-heat', 'pulse', 'purée', 'puree', 'reduce', 'refresh', 'reheat', 'roast', 'roll', 'rub in', 'sauté', 'saute', 'sear', 'sieve', 'simmer', 'slice', 'soak', 'steam', 'stew', 'sweat', 'whisk', 'zest']
	txt = value
	out = ""
	for bag in bags:
		x = re.search(""+bag+"", txt, re.IGNORECASE)
		if x != None:
			temp = re.split("[\\w\\S]*"+bag+"[\\w\\S]*", txt, 1, re.IGNORECASE)
			out = temp[1]
			break

	return out

# extract jargon
@register.simple_tag(name='jargon')
def jargon(value):
	txt = value
	bags = ['al dente', 'bake', 'baste', 'batch cooking', 'beat', 'blanch', 'blend', 'boil', 'braise', 'bring to the boil', 'caramelise', 'char grill', 'chop', 'chop finely', 'chop roughly', 'cream', 'deglaze', 'dice', 'dredge', 'drizzle', 'dry fry', 'flambé', 'flambe', 'fold', 'fried', 'fry', 'glaze', 'grate', 'grill', 'knead', 'line', 'lightly oil', 'marinate', 'par-boil', 'peel', 'poach', 'pre-heat', 'pulse', 'purée', 'puree', 'reduce', 'refresh', 'reheat', 'roast', 'roll', 'rub in', 'sauté', 'saute', 'sear', 'sieve', 'simmer', 'slice', 'soak', 'steam', 'stew', 'sweat', 'whisk', 'zest']
	out = ""
	for bag in bags:
		x = re.search(""+bag+"", txt, re.IGNORECASE)
		if x != None:
			temp = re.findall("[\\w\\S]*"+bag+"[\\w\\S]*", txt, re.IGNORECASE)
			out = temp[0]
			break

	return out

# url for jargon
@register.simple_tag(name='jar_url')
def jar_url(value):
	txt = value
	bags = ['al dente', 'bake', 'baste', 'batch cooking', 'beat', 'blanch', 'blend', 'boil', 'braise', 'bring to the boil', 'caramelise', 'char grill', 'chop', 'chop finely', 'chop roughly', 'cream', 'deglaze', 'dice', 'dredge', 'drizzle', 'dry fry', 'flambé', 'flambe', 'fold', 'fried', 'fry', 'glaze', 'grate', 'grill', 'knead', 'line', 'lightly oil', 'marinate', 'par-boil', 'peel', 'poach', 'pre-heat', 'pulse', 'purée', 'puree', 'reduce', 'refresh', 'reheat', 'roast', 'roll', 'rub in', 'sauté', 'saute', 'sear', 'sieve', 'simmer', 'slice', 'soak', 'steam', 'stew', 'sweat', 'whisk', 'zest']
	out = ""
	for bag in bags:
		x = re.search(""+bag+"", txt, re.IGNORECASE)
		if x != None:
			if bag == 'flambé':
				out = 'flambe'
			elif bag == 'fried':
				out = 'fry'
			elif bag == 'purée':
				out = 'puree'
			elif bag == 'sauté':
				out = 'saute'
			else:
				tbag = bag
				out = re.sub("\s", "", tbag)	
			break

	return out

# calculate % for review bars
@register.simple_tag(name='percent')
def percent(star, total):
	if total <= 0:
		out = 0
	else:
		temp = star/total
		out = round(temp*100, 2)
	return out

# for loop range
@register.filter(name='times')
def times(value):
	number = int(value)
	return range(number)

# subtract two numbers
@register.simple_tag(name="minus")
def minus(a, b):
	number = int(a) - int(b)
	return number

# restriction list
@register.simple_tag(name="rlist")
def rlist(username):
	out = Restriction.objects.filter(username=username).filter(check=True)
	return out

# try something new
@register.simple_tag(name="nlist")
def nlist(username):

	resobj = Restriction.objects.filter(username=username).exclude(check=0)

	ex = []

	for res in resobj:

		ex.append(str(res.ingr))

	uobj = User.objects.get(username=username)

	uid = uobj.id

	ratobj = Rating.objects.filter(user_id=uid)

	ex2 = []

	for rat in ratobj:

		ex2.append(rat.recipe_id)

	q = Q()

	for e in ex:
		q |= Q(Ingredients__icontains = e)


	out = Recipe.objects.exclude(id__in=ex2).exclude(q).order_by('?')

	return out[:5]


# similar
@register.simple_tag(name="slist")
def slist(username):
	resobj = Restriction.objects.filter(username=username).exclude(check=0)

	# exclude ingredient/tag
	ex = []

	for res in resobj:

		ex.append(str(res.ingr))

	uobj = User.objects.get(username=username)

	uid = uobj.id

	ratobj = Rating.objects.filter(user_id=uid)

	# similar tags
	incl = []

	# exclude rated recipes
	ex2 = []

	for rat in ratobj:

		recobj = Recipe.objects.get(id=rat.recipe_id)

		if recobj.tag not in incl:
			incl.append(recobj.tag)

		ex2.append(recobj.id)

	# excluded ingredients
	q1 = Q()

	for e in ex:
		q1 |= Q(Ingredients__icontains = e)

	out = Recipe.objects.exclude(q1).exclude(id__in=ex2).filter(tag__in=incl)

	return out[:5]
	

# top rated
@register.simple_tag(name="trlist")
def trlist(username):
	resobj = Restriction.objects.filter(username=username).exclude(check=0)

	ex = []

	for res in resobj:

		ex.append(str(res.ingr))

	q1 = Q()

	for e in ex:
		q1 |= Q(Ingredients__icontains = e)



	# requires foreign key Recipe has one-to-many relationship with Rating (check recipes.models.py) othertable__column

	nozero = Avg('rating__rating', exclude=Q(rating__rating=0))

	recobj = Recipe.objects.exclude(q1).annotate(rating_average=nozero).order_by('-rating_average')

	out = recobj

	return out[:5]

# most viewed
@register.simple_tag(name="mvlist")
def mvlist(username):
	resobj = Restriction.objects.filter(username=username).exclude(check=0)

	ex = []

	for res in resobj:

		ex.append(str(res.ingr))

	q1 = Q()

	for e in ex:
		q1 |= Q(Ingredients__icontains = e)

	out = Recipe.objects.exclude(q1).order_by('-recipes_view')

	return out[:5]

# check type of a variable
@register.simple_tag(name="ctype")
def ctype(value):

	out = str(type(value))

	return out

# len()
@register.simple_tag(name="lenlist")
def lenlist(thelist):

	temp = thelist

	out = len(temp)

	return out

# user_id to username
@register.filter(name='uname')
def uname(value):

	userobj = User.objects.get(id=value)

	out = userobj.username

	return out

# convert unit acronym to unit name
@register.filter(name='nunit')
def nunit(value):

	# this filter works like a switch statement

	return {
		'g': 'Gram',
		'kg': 'Kilogram',
		'oz': 'Ounce',
		'lb': 'Pound',
		'c': 'Cup',
		'foz': 'Fluid Ounce',
		'l': 'Liter',
		'ml': 'Mililiter',
		'qt': 'Quart',
		'tbsp': 'Tablespoon',
		'tsp': 'Teaspoon',
		'bb': 'Big Bottle',
		'b': 'Bottle',
		'cn': 'Can',
		'cv': 'Clove',
		'h': 'Head',
		'p': 'Pack',
		'pc': 'Piece',
		'po': 'Pouch',
		's': 'Stalk',
		'w': 'Whole',

	}.get(value)

# checks if the user has reviewed the recipe
@register.simple_tag(name='creview')
def creview(a, b):

	
	uid = a
	rid = b

	out = Rating.objects.filter(recipe_id=rid).filter(user_id=a).exists()


	return out

@register.simple_tag(name='mreview')
def mreview(a, b):

	uid = a
	rid = b

	out = Rating.objects.filter(recipe_id=rid).filter(user_id=a).get()

	return out

