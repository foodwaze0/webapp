from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.http import HttpResponse
import csv # CSV
import re # regular expression
from random import randrange # random number generator
from datetime import timedelta, datetime
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

from numpy import loadtxt, argmax
from keras.models import Sequential
from keras.layers import Dense
import numpy as np
from random import randrange
from keras.models import load_model, save_model
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping
from keras import backend as K
from scipy.stats import pearsonr
from sklearn.preprocessing import LabelEncoder

import os
from fractions import Fraction as frac
import math

# pagination
from django.core.paginator import Paginator

# don't forget to copy os.path.join(BASE_DIR, "templates") on settings TEMPLATES DIR

from .models import Recipe, Rating, Matrix, Ingredient
from inventories.models import Inventory
from accounts.models import Restriction
from django.contrib.auth.models import User
from .forms import RatingModelForm
from django.db.models import Avg, Max, Min, Sum, Q
from django.contrib.messages import get_messages


# Object Mixin to reduce redundancy
class RecipeObjectMixin(object):
	model = Recipe
	lookup = 'Title_link'


	def get_object(self):
		Title_link = self.kwargs.get('Title_link')
		obj = None
		if Title_link is not None:
			obj = get_object_or_404(self.model, Title_link=Title_link)
		return obj


class RecipeListView(View):

	template_name = "home.html"

	recipe_list = Recipe.objects.all()

	# recipe_list = Recipe.objects.all()

	# paginator = Paginator(recipe_list, 10)

	# page = request.GET.get('page')

	# recipes = paginator.get_page(page)

	# context = {
	# 	"recipes": recipes
	# }
	# return render(request, "home.html", context)

	def get_query(self):

		# u = self.check_user(self)
		if self.request.user.is_authenticated:
			
			res = Restriction.objects.filter(username=self.request.user.username).filter(check=1)

			ex = []

			for r in res:
				ex.append(str(r.ingr))

			# Restrictions

			q = Q()
			q2 = Q()

			# loops on each item for ex(excluded ingredients and tags can remove q2 if tags not included)
			for e in ex:
				# generate query
				q |= Q(Ingredients__icontains = e)
				q2 |= Q(tag__icontains = e)
			
			recipe_list = Recipe.objects.exclude(q).exclude(q2)

		else:
			recipe_list = Recipe.objects.all()

		return recipe_list

	def get(self, request, *args, **kwargs):
		paginator = Paginator(self.get_query(), 10)
		page = request.GET.get('page')
		recipes = paginator.get_page(page)
		context = {'recipes': recipes}
		return render(request, self.template_name, context)


class RecipeView(RecipeObjectMixin, View):

	template_name = "recipes/recipe_detail.html"

	def get(self, request, Title_link=None, *args, **kwargs):

		# add views to recipe
		robj = Recipe.objects.get(id=self.get_object().id)
		nview = int(robj.recipes_view)
		nview = nview+1
		robj.recipes_view = nview
		robj.save()

		serv = self.get_object().Servings
		temp = re.findall(r'\d+', serv)
		if len(temp) > 0:
			serv = int(temp[0])
		else:
			serv = 1
		sing = self.get_object().Ingredients
		ingr = sing.split("@")
		for key, ing in enumerate(ingr):
			txt = ing
			ning = re.sub("#", "", txt)
			ingr[key] = ning
		sinst = self.get_object().Instructions
		inst = sinst.split("@")
		rform = RatingModelForm()
		# Rating Reviews
		rview = Rating.objects.filter(recipe_id=self.get_object().id).exclude(rating=0)
		crating = rview.count()
		if crating == 0:
			avg = 0
		else:
			avg = rview.aggregate(Avg('rating'))
			avg = round(avg['rating__avg'], 2)
		star5 = Rating.objects.filter(recipe_id=self.get_object().id).filter(rating=5).count()
		star4 = Rating.objects.filter(recipe_id=self.get_object().id).filter(rating=4).count()
		star3 = Rating.objects.filter(recipe_id=self.get_object().id).filter(rating=3).count()
		star2 = Rating.objects.filter(recipe_id=self.get_object().id).filter(rating=2).count()
		star1 = Rating.objects.filter(recipe_id=self.get_object().id).filter(rating=1).count()

		context = {
			'recipe': self.get_object(),
			'serv': serv,
			'ingr': ingr,
			'inst': inst,
			'rform': rform,
			'rview': rview,
			'crating': crating,
			'avg': avg,
			'star5': star5,
			'star4': star4,
			'star3': star3,
			'star2': star2,
			'star1': star1,
			}

		return render(request, self.template_name, context)

	def post(self, request, Title_link=None, *args, **kwargs):

		serv = self.get_object().Servings
		temp = re.findall(r'\d+', serv)
		if len(temp) > 0:
			serv = int(temp[0])
		else:
			serv = 1
		sing = self.get_object().Ingredients
		ingr = sing.split("@")
		for key, ing in enumerate(ingr):
			txt = ing
			ning = re.sub("#", "", txt)
			ingr[key] = ning
		sinst = self.get_object().Instructions
		inst = sinst.split("@")
		rform = RatingModelForm()
		# Rating Reviews
		rview = Rating.objects.filter(recipe_id=self.get_object().id).exclude(rating=0)
		crating = rview.count()
		if crating == 0:
			avg = 0
		else:
			avg = rview.aggregate(Avg('rating'))
			avg = round(avg['rating__avg'], 2)
		star5 = Rating.objects.filter(recipe_id=self.get_object().id).filter(rating=5).count()
		star4 = Rating.objects.filter(recipe_id=self.get_object().id).filter(rating=4).count()
		star3 = Rating.objects.filter(recipe_id=self.get_object().id).filter(rating=3).count()
		star2 = Rating.objects.filter(recipe_id=self.get_object().id).filter(rating=2).count()
		star1 = Rating.objects.filter(recipe_id=self.get_object().id).filter(rating=1).count()


		if request.POST.get("frmId") == "rate":

			rform = RatingModelForm(request.POST)
			
			rform.instance.recipe_id = self.get_object().id
			rform.instance.user_id = self.request.user.id
			star = request.POST.get('star')
			if star is None:
				star = 0
			rform.instance.rating = star

			if rform.is_valid():

				uid = request.user.id
				rid = self.get_object().id

				if Matrix.objects.filter(user_id=uid).exists():
					mobj = Matrix.objects.get(user_id=uid)

					txt = mobj.rating_list

					arr = txt.split("@")

					counter = 0

					for a in arr:

						if counter == rid-1:
							arr[counter] = str(star)
							break
						else:
							counter += 1

					new = "@".join(arr)
					mobj.rating_list = new
					mobj.save()
					
				else:
					rtstr = ""

					for x in range(1, 1141, 1):

						if x == rid:
							urating = star

						else:
							if Rating.objects.filter(user_id=uid).filter(recipe_id=x).exists():
								rtobj = Rating.objects.filter(user_id=uid).filter(recipe_id=x).get()
								urating = rtobj.rating
							else:
								urating = 0

						if rtstr == "":
							rtstr = str(urating)
						else:
							tstr = "@"+str(urating)
							rtstr = rtstr+tstr

					
					new = Matrix(user_id=uid, rating_list=rtstr)
					new.save()

				rform.save()


		# start of cook
		elif request.POST.get("frmId") == "cook":
			data = request.POST.dict()
			# print("Cooked Recipe")
			# servings
			srv = int(data['snum'])
			# recipe id
			recid = self.get_object().id
			# username
			uname = request.user.username
			
			ingobj = Ingredient.objects.filter(recipe_id=recid)
			invobj = Inventory.objects.filter(username=uname)
			# recipe servings
			isrv = int(pint(self.get_object().Servings))

			invd = {}
			# to add to dictionary
			# invd[key] = value


			# validation
			for i in ingobj:
				name = i.name
				# remove start and end space
				name = name.lstrip()
				name = name.rstrip()
				iunit = i.unit
				iqty = i.qty
				rsrv = srv/isrv

				imass = Mass(iunit)
				ivol = Volume(iunit)
				ioth = Others(iunit)
				aunit = Acro(iunit)


				for iv in invobj:
					ivid = iv.id
					ivname = iv.ingr
					ivname = ivname.lstrip()
					ivname = ivname.rstrip()


					if name.lower() == ivname.lower():
						ivunit = iv.unit
						ivqty = iv.qty

						ivmass = Mass(ivunit)
						ivvol = Volume(ivunit)
						ivoth = Others(ivunit)

						ivfrac = False

						# start mass
						if imass == True and ivmass == True:

							if checkfrac(iqty) == True:
								iqty = frac2dec(iqty)

							if checkfrac(ivqty) == True:
								ivfrac = True
								ivqty = frac2dec(ivqty)

							ivqty = float(ivqty)

							# convert recipe unit to inventory unit
							coniqty = conMass(float(iqty), aunit, ivunit)

							# calculate quantity by servings
							rqty = rsrv*coniqty

							# check if inventory quantity is enough
							if ivqty >= rqty:
								uqty = ivqty - rqty
								# print(ivqty, rqty, uqty)

								if ivfrac == True:
								 	uqty = dec2frac(uqty)
								 	invd[ivid] = uqty
								else:
									invd[ivid] = round(uqty, 2)


							else:
								
								msgstr = name+' Insuficient Quantity'
								messages.error(request, msgstr)


						# end mass

						# start volume
						elif ivol == True and ivvol == True:
							
							if checkfrac(iqty) == True:
								iqty = frac2dec(iqty)

							if checkfrac(ivqty) == True:
								ivfrac = True
								ivqty = frac2dec(ivqty)

							ivqty = float(ivqty)

							# convert recipe unit to inventory unit
							coniqty = conVolume(float(iqty), aunit, ivunit)

							# calculate quantity by servings
							rqty = rsrv*coniqty

							# check if inventory quantity is enough
							if ivqty >= rqty:
								uqty = ivqty - rqty
								# print(ivqty, rqty, uqty)

								if ivfrac == True:
								 	uqty = dec2frac(uqty)
								 	invd[ivid] = uqty
								else:
								 	invd[ivid] = round(uqty, 2)


							else:
								
								msgstr = name+' Insuficient Quantity'
								messages.error(request, msgstr)

						# end volume

						# start others
						elif ioth == True and ivoth == True:
							
							if checkfrac(iqty) == True:
								iqty = frac2dec(iqty)

							if checkfrac(ivqty) == True:
								ivfrac = True
								ivqty = frac2dec(ivqty)

							ivqty = float(ivqty)

							# calculate quantity by servings
							rqty = rsrv*float(iqty)

							# check if inventory quantity is enough
							if ivqty >= rqty:

								uqty = ivqty - rqty

								# print(ivqty, rqty, uqty)

								if ivfrac == True:
								 	uqty = dec2frac(uqty)
								 	invd[ivid] = uqty
								else:
								 	invd[ivid] = round(uqty, 2)


							else:
								
								msgstr = name+' Insuficient Quantity'
								messages.error(request, msgstr)

						# end others
						else:
							if aunit != 'nothing':
								msgstr = name+' Invalid Unit'
								messages.error(request, msgstr)

						break

				# end of invobj		
				else:
					msgstr = name+' not found in inventory'
					messages.error(request, msgstr)

			# end of validation

			# updating inventory
			storage = get_messages(request)
			if len(storage) == 0:
				for key, val in invd.items():
					# print('Key',key)
					# print('Value',val)
					uinvobj = Inventory.objects.get(id=key)
					uinvobj.qty = val
					uinvobj.save()

				# add cook to recipe
				robj = Recipe.objects.get(id=self.get_object().id)
				ncook = int(robj.cook)
				ncook = ncook+1
				robj.cook = ncook
				robj.save()


			

		# end of cook

		context = {
			'recipe': self.get_object(),
			'serv': serv,
			'ingr': ingr,
			'inst': inst,
			'rform': rform,
			'rview': rview,
			'crating': crating,
			'avg': avg,
			'star5': star5,
			'star4': star4,
			'star3': star3,
			'star2': star2,
			'star1': star1,
			}
		
		return render(request, self.template_name, context)


def JargonView(request, *args, **kwargs):

	return render(request, "jargon.html", {})


def AboutView(request, *args, **kwargs):

	return render(request, "about.html", {})	


def BeefView(request, *args, **kwargs):

	tag = "Beef"

	if request.user.is_authenticated:
			
		res = Restriction.objects.filter(username=request.user.username).filter(check=1)

		ex = []

		for r in res:
			ex.append(str(r.ingr))

		q = Q()
			
		for e in ex:
				
			q |= Q(Ingredients__icontains = e)
			q |= Q(tag__icontains = e)

		recipeobj = Recipe.objects.exclude(q).filter(tag__icontains = tag)

	else:

		recipeobj = Recipe.objects.filter(q).filter(tag__icontains = tag)

	paginator = Paginator(recipeobj, 10)
	page = request.GET.get('page')
	recipes = paginator.get_page(page)

	context = {
		'recipes': recipes,
		'tag': tag,
	}


	return render(request, "tag.html", context)


def DessertView(request, *args, **kwargs):

	tag = "Dessert"

	if request.user.is_authenticated:
			
		res = Restriction.objects.filter(username=request.user.username).filter(check=1)

		ex = []

		for r in res:
			ex.append(str(r.ingr))

		q = Q()
			
		for e in ex:
				
			q |= Q(Ingredients__icontains = e)
			q |= Q(tag__icontains = e)

		recipeobj = Recipe.objects.exclude(q).filter(tag__icontains = tag)

	else:

		recipeobj = Recipe.objects.filter(q).filter(tag__icontains = tag)

	paginator = Paginator(recipeobj, 10)
	page = request.GET.get('page')
	recipes = paginator.get_page(page)
	

	context = {
		'recipes': recipes,
		'tag': tag,
	}


	return render(request, "tag.html", context)


def FishView(request, *args, **kwargs):

	tag = "Fish"

	if request.user.is_authenticated:
			
		res = Restriction.objects.filter(username=request.user.username).filter(check=1)

		ex = []

		for r in res:
			ex.append(str(r.ingr))

		q = Q()
			
		for e in ex:
				
			q |= Q(Ingredients__icontains = e)
			q |= Q(tag__icontains = e)

		recipeobj = Recipe.objects.exclude(q).filter(tag__icontains = tag)

	else:

		recipeobj = Recipe.objects.filter(q).filter(tag__icontains = tag)

	paginator = Paginator(recipeobj, 10)
	page = request.GET.get('page')
	recipes = paginator.get_page(page)
	

	context = {
		'recipes': recipes,
		'tag': tag,
	}


	return render(request, "tag.html", context)


def NoodleView(request, *args, **kwargs):

	tag = "Noodle"

	if request.user.is_authenticated:
			
		res = Restriction.objects.filter(username=request.user.username).filter(check=1)

		ex = []

		for r in res:
			ex.append(str(r.ingr))

		q = Q()
			
		for e in ex:
				
			q |= Q(Ingredients__icontains = e)
			q |= Q(tag__icontains = e)

		recipeobj = Recipe.objects.exclude(q).filter(tag__icontains = tag)

	else:

		recipeobj = Recipe.objects.filter(q).filter(tag__icontains = tag)

	paginator = Paginator(recipeobj, 10)
	page = request.GET.get('page')
	recipes = paginator.get_page(page)
	

	context = {
		'recipes': recipes,
		'tag': tag,
	}


	return render(request, "tag.html", context)


def PorkView(request, *args, **kwargs):

	tag = "Pork"

	if request.user.is_authenticated:
			
		res = Restriction.objects.filter(username=request.user.username).filter(check=1)

		ex = []

		for r in res:
			ex.append(str(r.ingr))

		q = Q()
			
		for e in ex:
				
			q |= Q(Ingredients__icontains = e)
			q |= Q(tag__icontains = e)

		recipeobj = Recipe.objects.exclude(q).filter(tag__icontains = tag)

	else:

		recipeobj = Recipe.objects.filter(q).filter(tag__icontains = tag)

	paginator = Paginator(recipeobj, 10)
	page = request.GET.get('page')
	recipes = paginator.get_page(page)
	

	context = {
		'recipes': recipes,
		'tag': tag,
	}


	return render(request, "tag.html", context)


def PoultryView(request, *args, **kwargs):

	tag = "Poultry"

	if request.user.is_authenticated:
			
		res = Restriction.objects.filter(username=request.user.username).filter(check=1)

		ex = []

		for r in res:
			ex.append(str(r.ingr))

		q = Q()
			
		for e in ex:
				
			q |= Q(Ingredients__icontains = e)
			q |= Q(tag__icontains = e)

		recipeobj = Recipe.objects.exclude(q).filter(tag__icontains = tag)

	else:

		recipeobj = Recipe.objects.filter(q).filter(tag__icontains = tag)

	paginator = Paginator(recipeobj, 10)
	page = request.GET.get('page')
	recipes = paginator.get_page(page)
	

	context = {
		'recipes': recipes,
		'tag': tag,
	}


	return render(request, "tag.html", context)


def RiceView(request, *args, **kwargs):

	tag = "Rice"

	if request.user.is_authenticated:
			
		res = Restriction.objects.filter(username=request.user.username).filter(check=1)

		ex = []

		for r in res:
			ex.append(str(r.ingr))

		q = Q()
			
		for e in ex:
				
			q |= Q(Ingredients__icontains = e)
			q |= Q(tag__icontains = e)

		recipeobj = Recipe.objects.exclude(q).filter(tag__icontains = tag)

	else:

		recipeobj = Recipe.objects.filter(q).filter(tag__icontains = tag)

	paginator = Paginator(recipeobj, 10)
	page = request.GET.get('page')
	recipes = paginator.get_page(page)
	

	context = {
		'recipes': recipes,
		'tag': tag,
	}


	return render(request, "tag.html", context)


def SeafoodView(request, *args, **kwargs):

	tag = "Seafood"

	if request.user.is_authenticated:
			
		res = Restriction.objects.filter(username=request.user.username).filter(check=1)

		ex = []

		for r in res:
			ex.append(str(r.ingr))

		q = Q()
			
		for e in ex:
				
			q |= Q(Ingredients__icontains = e)
			q |= Q(tag__icontains = e)

		recipeobj = Recipe.objects.exclude(q).filter(tag__icontains = tag)

	else:

		recipeobj = Recipe.objects.filter(q).filter(tag__icontains = tag)

	paginator = Paginator(recipeobj, 10)
	page = request.GET.get('page')
	recipes = paginator.get_page(page)
	

	context = {
		'recipes': recipes,
		'tag': tag,
	}


	return render(request, "tag.html", context)


def VegetableView(request, *args, **kwargs):

	tag = "Vegetable"

	if request.user.is_authenticated:
			
		res = Restriction.objects.filter(username=request.user.username).filter(check=1)

		ex = []

		for r in res:
			ex.append(str(r.ingr))

		q = Q()
			
		for e in ex:
				
			q |= Q(Ingredients__icontains = e)
			q |= Q(tag__icontains = e)

		recipeobj = Recipe.objects.exclude(q).filter(tag__icontains = tag)

	else:

		recipeobj = Recipe.objects.filter(q).filter(tag__icontains = tag)

	paginator = Paginator(recipeobj, 10)
	page = request.GET.get('page')
	recipes = paginator.get_page(page)
	

	context = {
		'recipes': recipes,
		'tag': tag,
	}


	return render(request, "tag.html", context)


def Search(request, *args, **kwargs):


	# initialize wordstr in case of using /search url

	wordsstr = ""

	# checking if it is posted first before generating query to search
	# if request.method == 'POST':
	if request.POST.get("frmId") == "srch":
		data = request.POST.dict()
		wordsstr = data['txtsearch']

		# if entered word is null or space
		if wordsstr == "" or wordsstr == " ":

			return redirect('home')

		words = wordsstr.split(" ")

	# else redirect to home
	else:

		return redirect('home')

	q = Q()

	for w in words:
		# q |= Q(id__icontains = w)
		q |= Q(Recipe__icontains = w)
		q |= Q(Ingredients__icontains = w)
		q |= Q(Instructions__icontains = w)
		q |= Q(tag__icontains = w)

	# if a user is logged in it will check for restricted ingredients
	if request.user.is_authenticated:
			
		res = Restriction.objects.filter(username=request.user.username).filter(check=1)

		ex = []

		for r in res:
			ex.append(str(r.ingr))

		q2 = Q()
			
		for e in ex:
				
			q2 |= Q(Ingredients__icontains = e)
			q2 |= Q(tag__icontains = e)

		recipeobj = Recipe.objects.filter(q).exclude(q2)

	else:

		recipeobj = Recipe.objects.filter(q)

	recipeobj = Recipe.objects.filter(q)

	paginator = Paginator(recipeobj, 10)
	page = request.GET.get('page')
	recipes = paginator.get_page(page)

	context = {
		'recipes': recipes,
		'words': wordsstr,
	}

	return render(request, "recipes/result.html", context)


def RecommendList(request, *args, **kwargs):

	context = {}

	
	# ingredients to be used

	inq = Q()
	ingrlist = []

	if request.method == 'POST':
		data = request.POST.getlist('ingrc')

		invobj = Inventory.objects.filter(id__in=data)

		for i in invobj:

			ingrlist.append(i.ingr)


		for l in ingrlist:

			inq |= Q(Ingredients__icontains = l)


	if request.user.is_authenticated:
			
		# ingredients to be excluded

		res = Restriction.objects.filter(username=request.user.username).filter(check=1)

		ex = []

		for r in res:
			ex.append(str(r.ingr))

		exq = Q()
			
		for e in ex:
				
			exq |= Q(Ingredients__icontains = e)
			exq |= Q(tag__icontains = e)


		
		top5 = Algorithm(request)

		# print(top5)


		ratobj = Rating.objects.filter(user_id__in=top5).exclude(rating__lt=3)

		rc = []

		for rt in ratobj:
			# print(rt.recipe_id)
			# print(rt.rating)
			if rt.recipe_id not in rc:
				rc.append(rt.recipe_id)

		recipeobj = Recipe.objects.filter(id__in=rc).filter(inq).exclude(exq)

		# recipeobj = Recipe.objects.exclude(exq).filter(inq)

	'''

	else:

		recipeobj = Recipe.objects.filter(q)

	'''


	paginator = Paginator(recipeobj, 10)
	page = request.GET.get('page')
	recipes = paginator.get_page(page)

	context = {
		'recipes': recipes,
		'ingrlist': ingrlist,
	}

	return render(request, "recipes/recommend_list.html", context)



def dec2bin(value_list):

	num = value_list.astype(int)

	output = np.array([])

	# converting rating to binary

	for x in num:

		if x == 0:
			new = np.array([1,0,0,0,0,0])
		elif x == 1:
			new = np.array([0,1,0,0,0,0])
		elif x == 2:
			new = np.array([0,0,1,0,0,0])
		elif x == 3:
			new = np.array([0,0,0,1,0,0])
		elif x == 4:
			new = np.array([0,0,0,0,1,0])
		elif x == 5:
			new = np.array([0,0,0,0,0,1])

		if len(output) > 0:
			output = np.vstack((output, new))
		else:
			output = np.array(new)

	# real dec2bin
	'''
	num = value_list.astype(int)
	output = np.array([])
	counter = 1
	for x in num:
		tnum = x
		storage = np.array([])
		new = np.array([])

		while True:
			if tnum > 1:
				temp = int(tnum % 2)
				tnum = int(tnum / 2)
				storage = np.append(storage, temp)
			else:
				storage = np.append(storage, tnum)
				break

		lenout = len(storage)
		# +1 to add more number of user 10 = 1023 user limit
		if lenout < 10:
			while True:
				check = len(storage)
				if check < 10:
					storage = np.append(storage, 0)
				else:
					break

		new = storage[::-1]
		if len(output) > 0:
			output = np.vstack((output, new))
		else:
			output = np.array(new)

	'''

	# print("Num:\n", num[0:5])
	# print("Output:\n", output[0:5])

	return output


def ManageView(request, *args, **kwargs):
	context = {}

	if request.method == 'POST':

		if 'rating' in request.POST:
			# users = ['Joe', 'Julius', 'Vincent', 'Oliver', 'Jack', 'Harry', 'Jacob', 'Charlie', 'Thomas', 'George', 'Leo', 'James', 'William', 'Noah', 'Liam', 'Mason', 'Ethan', 'Michael', 'Alexander', 'Daniel', 'Charles', 'David']

			users = User.objects.exclude(id=1)
			tags = ['Beef', 'Dessert', 'Fish', 'Noodle', 'Pork', 'Poultry', 'Rice', 'Seafood', 'Vegetable']
			pos = ['Nice!', 'I like it!', 'It tastes great!', 'Good!', 'Love it!']
			neg = ['Horrible!', "I don't like it", "It doesn't taste great", "Bad!", 'Hate it!']

			# change the value of 2nd parameter to the number of random data you want to generate
			# for x in range(0, 200, 1):
			# 	nuser = randrange(0, 21)
			# 	name = users[nuser]
			# 	rate = randrange(1, 5)
			# 	nrev = randrange(0, 4)
			# 	# random date generator sdate = start edate = end
			# 	sdate = datetime.strptime('1/1/2019 12:00 AM', '%m/%d/%Y %I:%M %p')
			# 	edate = datetime.strptime('12/31/2019 11:59 PM', '%m/%d/%Y %I:%M %p')
			# 	delta = edate - sdate
			# 	int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
			# 	random_second = randrange(int_delta)
			# 	date = sdate + timedelta(seconds=random_second)
			# 	if rate >=3:
			# 		review = pos[nrev]
			# 	else:
			# 		review = neg[nrev]
			# 	check = False
			# 	while check == False:
			# 		recipe = randrange(1, 1140) # range of recipe id 1-1140
			# 		test = Rating.objects.filter(recipe_id=recipe).filter(username=name)
			# 		if test.count() == 0:
			# 			check = True
			# 	# recipe chosen
			# 	chosen = Recipe.objects.get(id=recipe)
			# 	ccook = chosen.cook
			# 	cviews = chosen.recipes_view
			# 	# max
			# 	mcook = Recipe.objects.all().aggregate(Max('cook'))
			# 	mcook = mcook['cook__max']
			# 	mviews = Recipe.objects.all().aggregate(Max('recipes_view'))
			# 	mviews = mviews['recipes_view__max']
			# 	cook = (ccook/mcook)*5
			# 	view = (cviews/mviews)*5
			# 	overall = int(round((rate+cook+view)/3, 0))
			# 	new = Rating(recipe_id=recipe, username=name, rating=rate, orating=overall, review=review, posted_at=date)
			# 	new.save()
			
			for u in users:
				brate = randrange(1, 6)
				drate = randrange(1, 6)
				frate = randrange(1, 6)
				nrate = randrange(1, 6)
				pkrate = randrange(1, 6)
				pyrate = randrange(1, 6)
				rrate = randrange(1, 6)
				srate = randrange(1, 6)
				vrate = randrange(1, 6)
				erate = randrange(1, 6)
				# change 2nd parameter to for number of ratings generated for each user
				for x in range(0, 400, 1):
					# random review
					nrev = randrange(0, 5)
					# recipe id
					check = False
					while check == False:
						recipe = randrange(1, 1141) # range of recipe id 1-1140 +1 to include the limit you want
						test = Rating.objects.filter(recipe_id=recipe).filter(user_id=u.id)
						if test.count() == 0:
							check = True

					# rate
					robj = Recipe.objects.get(id=recipe)
					if str(robj.tag) == 'Beef':
						rate = brate
					elif str(robj.tag) == 'Dessert':
						rate = drate
					elif str(robj.tag) == 'Fish':
						rate = frate
					elif str(robj.tag) == 'Noodle':
						rate = nrate
					elif str(robj.tag) == 'Pork':
						rate = pkrate
					elif str(robj.tag) == 'Poultry':
						rate = pyrate
					elif str(robj.tag) == 'Rice':
						rate = rrate
					elif str(robj.tag) == 'Seafood':
						rate = srate
					elif str(robj.tag) == 'Vegetable':
						rate = vrate
					else:
						rate = erate

					# review
					if rate >=3:
						review = pos[nrev]
					else:
						review = neg[nrev]

					# random date
					sdate = datetime.strptime('1/1/2019 12:00 AM', '%m/%d/%Y %I:%M %p')
					edate = datetime.strptime('12/31/2019 11:59 PM', '%m/%d/%Y %I:%M %p')
					delta = edate - sdate
					int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
					random_second = randrange(int_delta)
					date = sdate + timedelta(seconds=random_second)

					new = Rating(recipe_id=recipe, rating=rate, review=review, posted_at=date, user_id=u.id)
					new.save()

			messages.success(request, 'Ratings updated.')
			# end of Rating

		elif 'encode' in request.POST:

			# recipes = Recipe.objects.filter(pk__in=[1,2,3])
			recipes = Recipe.objects.all()

			for r in recipes:
				# print(r.id)
				ting = r.Ingredients
				ingr = ting.split("@")
				arrunit = ["pouches", "pouch", "cloves", "clove", "stalk(s)", "stalks", "stalk", "tablespoons", "tablespoon", "teaspoons", "teaspoon", "tbsps.", "tbsps", "tbsp.", "tbsp", "tsps.", "tsp.", "tsps", "tsp", "cup(s)", "cups", "cup", "bunches", "bunch", "packs", "package", "pack", "big bottle", "bottle", "pounds", "pound", "lbs.", "lbs", "lb.", "lb", "ounce(s)", "ounces", "ounce", "can(s)", "cans", "can", "ozs.", "ozs", "oz.", "oz", "piece(s)", "pieces", "piece", "pcs.", "pcs", "pc.", "mililiters", "mililiter", "liters", "liter", "kilograms", "kilogram", "grams", "gram", "quarts", "quart", "whole", "head"]

				for key, ing in enumerate(ingr):
					# ingr[key] = 'new value'
					quantity = ''
					unit = ''
					name = ''
					ext = ''
					curr = ing.lstrip()

					if "#" in curr:
						text = re.split("\#", curr)
						curr = text[0].lstrip()
						ext = text[1].lstrip()

					check = re.search("^(\d+\s)?\d+\/\d+|^\d+(\.\d+)?", curr)

					if check:
						quantity = check.group()
						tcurr = re.split("^(\d+\s)?\d+\/\d+|^\d+(\.\d+)?", curr)
						name = str(tcurr[3]).lstrip()
						
						for u in arrunit:
							if re.search("^"+re.escape(u), name, flags=re.IGNORECASE):
								unit = u
								tname = re.split(re.escape(u), name, flags=re.IGNORECASE)
								name = tname[1].lstrip()
								break
					else:
						name = curr

					new = Ingredient(recipe_id=r.id, name=name, qty=quantity, unit=unit, ext=ext)
					new.save()
			
			messages.success(request, 'Ingredients Encoded')
			# end of encode

		elif 'users' in request.POST:

			
			users = ['Julius', 'Vincent', 'Oliver', 'Jack', 'Harry', 'Jacob', 'Charlie', 'Thomas', 'George', 'Leo', 'James', 'William', 'Noah', 'Liam', 'Mason', 'Ethan', 'Michael', 'Alexander', 'Daniel', 'Charles', 'David']
			password = 'wew12345'

			for u in users:
				new = User.objects.create_user(u, 'example@example.com', password)
				new.save()

			messages.success(request, 'Users Registered')
			

			# end of users

		elif 'csv' in request.POST:
			# Create the HttpResponse object with the appropriate CSV header.
		    response = HttpResponse(content_type='text/csv')
		    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

		    writer = csv.writer(response)
		    # set range of rating id
		    # obj = Rating.objects.filter(id__range=(1, 10))
		    uobj = User.objects.exclude(id=1)
		    robj = Recipe.objects.all()
		    tags = ['Beef', 'Dessert', 'Fish', 'Noodle', 'Pork', 'Poultry', 'Rice', 'Seafood', 'Vegetable']

		    # fixed

		    for t in tags:
		    	ttag = t
		    	if ttag == 'Beef':
		    		tag = 1
		    	elif ttag == 'Dessert':
		    		tag = 2
		    	elif ttag == 'Fish':
		    		tag = 3
		    	elif ttag == 'Noodle':
		    		tag = 4
		    	elif ttag == 'Pork':
		    		tag = 5
		    	elif ttag == 'Poultry':
		    		tag = 6
		    	elif ttag == 'Rice':
		    		tag = 7
		    	elif ttag == 'Seafood':
		    		tag = 8
		    	elif ttag == 'Vegetable':
		    		tag = 9
		    	else:
		    		tag = 0

		    	# 1 to 3 inp1 1 = 1-0, 2 = 2-3, 3 = 4-5

		    	'''

		    	for i in range(1, 3, 1):
		    		inp1 = i


		    		# 0-1 rating
		    		if inp1 == 1:
		    			for o in range(2):
		    				output = o
		    				writer.writerow([inp1, tag, output])

		    		#  2-3 rating
		    		elif inp1 == 2:
		    			for p in range(2, 4, 1):
		    				output = p
		    				writer.writerow([inp1, tag, output])

		    		#  4-5 rating		
		    		else:
		    			for q in range(4, 6, 1):
		    				output = q
		    				writer.writerow([inp1, tag, output])
		    	'''

		    	for i in range(0, 6, 1):
		    		inp1 = i

		    		for i2 in range(0, 6, 1):
		    				inp2 = i2
		    				tout = (inp1+inp2)/2
		    				output = int(round(tout, 0))
		    				writer.writerow([inp1, inp2, tag, output])

		    				
		    # random but based on users

		    '''
		    for u in uobj:
		    	# user id
		    	uid = u.id
		    	
		    	for t in tags:
		    		ttag = t
		    		
		    		if ttag == 'Beef':
			    		tag = 1
			    	elif ttag == 'Dessert':
			    		tag = 2
			    	elif ttag == 'Fish':
			    		tag = 3
			    	elif ttag == 'Noodle':
			    		tag = 4
			    	elif ttag == 'Pork':
			    		tag = 5
			    	elif ttag == 'Poultry':
			    		tag = 6
			    	elif ttag == 'Rice':
			    		tag = 7
			    	elif ttag == 'Seafood':
			    		tag = 8
			    	elif ttag == 'Vegetable':
			    		tag = 9
			    	else:
			    		tag = 0

			    	

		    		robj = Recipe.objects.filter(tag__icontains=ttag)

		    		rlist = []

		    		for r in robj:
		    			rid = r.id
		    			rlist.append(rid)

		    		rtobj = Rating.objects.filter(user_id=uid).filter(recipe_id__in=rlist)

		    		total = rtobj.count()

		    		

		    		if total == 0:

		    			inp1 = 1
		    			output = 0
		    			

		    		else:

			    		sums = 0

			    		for rt in rtobj:
			    			nums = int(rt.rating)
			    			sums += nums

			    		

			    		tavg = sums/total

			    		avg = round(tavg, 0)

			    		avg = int(avg)

			    		

				    	if avg > 2 and avg <= 5:
				    		inp1 = 2
				    		output = randrange(3, 6)

				    	elif avg > 5:
				    		inp1 = 2
				    		output = randrange(3, 6)

				    	else:
				    		inp1 = 1
				    		output = randrange(1, 3)
				    		

		    		writer.writerow([inp1, tag, output])
			'''


			# writer.writerow([inp1, tag, output])

		    messages.success(request, 'CSV File Generated')
		    return response

		elif 'avg' in request.POST:

			obj = Rating.objects.exclude(rating=0)

			# rlist = []

			# for x in obj:

			# 	rid = x.recipe_id
			# 	if rid not in rlist:
			# 		rlist.append(rid)


			# recipes = Recipe.objects.filter(pk__in=rlist)

			mntag = 1
			mxtag = 9
			mnuser = obj.aggregate(Min('user_id'))
			mnuser = mnuser['user_id__min']
			mxuser = obj.aggregate(Max('user_id'))
			mxuser = mxuser['user_id__max']


			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

			writer = csv.writer(response)
			"""
			for x in obj:
				# user
				cuser = x.user_id
				# user = (cuser - mnuser)/(mxuser - mnuser)
				user = str(cuser)

				# tag
				recipe = Recipe.objects.get(id=x.recipe_id)
				ttag = recipe.tag

				if ttag == 'Beef':
					# ctag = 1
					# ctag = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
					ctag = ttag
				elif ttag == 'Dessert':
					# ctag = 2
					# ctag = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
					ctag = ttag
				elif ttag == 'Fish':
					# ctag = 3
					# ctag = [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
					ctag = ttag
				elif ttag == 'Noodle':
					# ctag = 4
					# ctag = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
					ctag = ttag
				elif ttag == 'Pork':
					# ctag = 5
					# ctag = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
					ctag = ttag
				elif ttag == 'Poultry':
					# ctag = 6
					# ctag = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
					ctag = ttag
				elif ttag == 'Rice':
					# ctag = 7
					# ctag = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
					ctag = ttag
				elif ttag == 'Seafood':
					# ctag = 8
					# ctag = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
					ctag = ttag
				elif ttag == 'Vegetable':
					# ctag = 9
					# ctag = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
					ctag = ttag
				else:
					# ctag = 0
					ctag = 'none'
				
				# tag = (ctag - mntag)/(mxtag - mntag)
				tag = ttag
				mnout = 1
				mxout = 5
				# out = (int(x.rating) - mnout)/(mxout - mnout)
				out = x.rating

				writer.writerow([user, ctag, out])
			"""


			for x in range(1, 100, 1):

				c = int(randrange(1, 4))

				# int1 = 1
				# int2 = 1
				# out = 1

				
				if c == 1:
					inpt = randrange(1, 51)
					int1 = inpt
					int2 = inpt
					out = 1
				elif c == 2:
					inpt = randrange(51, 101)
					int1 = inpt
					int2 = inpt
					out = 100
				else:
					inpt = randrange(101, 151)
					int1 = inpt
					int2 = inpt
					out = 150

				writer.writerow([int1, int2, out])


			# for x in range(1, 11, 1):
			# 	crating = Rating.objects.filter(recipe_id=x)
			# 	trating = crating.aggregate(Avg('rating'))
			# 	out = trating['rating__avg']
			# 	print(out)

			messages.success(request, 'Calculated Average')
			return response

		elif 'test' in request.POST:

			# print('test')

			otag1obj = Recipe.objects.filter(tag__icontains='Beef')
			otag1avg = otag1obj.aggregate(Avg('rating__rating'))
			print(otag1avg)
			otag1 = int(round(otag1avg['rating__rating__avg'], 0))
			print(otag1)

			otag2obj = Recipe.objects.filter(tag__icontains='Dessert')
			otag2avg = otag2obj.aggregate(Avg('rating__rating'))
			print(otag2avg)
			otag2 = int(round(otag2avg['rating__rating__avg'], 0))
			print(otag2)

			otag3obj = Recipe.objects.filter(tag__icontains='Fish')
			otag3avg = otag3obj.aggregate(Avg('rating__rating'))
			print(otag3avg)
			otag3 = int(round(otag3avg['rating__rating__avg'], 0))
			print(otag3)

			otag4obj = Recipe.objects.filter(tag__icontains='Noodle')
			otag4avg = otag4obj.aggregate(Avg('rating__rating'))
			print(otag4avg)
			otag4 = int(round(otag4avg['rating__rating__avg'], 0))
			print(otag4)

			otag5obj = Recipe.objects.filter(tag__icontains='Pork')
			otag5avg = otag5obj.aggregate(Avg('rating__rating'))
			print(otag5avg)
			otag5 = int(round(otag5avg['rating__rating__avg'], 0))
			print(otag5)

			otag6obj = Recipe.objects.filter(tag__icontains='Poultry')
			otag6avg = otag6obj.aggregate(Avg('rating__rating'))
			print(otag6avg)
			otag6 = int(round(otag6avg['rating__rating__avg'], 0))
			print(otag6)

			otag7obj = Recipe.objects.filter(tag__icontains='Rice')
			otag7avg = otag7obj.aggregate(Avg('rating__rating'))
			print(otag7avg)
			otag7 = int(round(otag7avg['rating__rating__avg'], 0))
			print(otag7)

			otag8obj = Recipe.objects.filter(tag__icontains='Seafood')
			otag8avg = otag8obj.aggregate(Avg('rating__rating'))
			print(otag8avg)
			otag8 = int(round(otag8avg['rating__rating__avg'], 0))
			print(otag8)

			otag9obj = Recipe.objects.filter(tag__icontains='Vegetable')
			otag9avg = otag9obj.aggregate(Avg('rating__rating'))
			print(otag9avg)
			otag9 = int(round(otag9avg['rating__rating__avg'], 0))
			print(otag9)

			print(request.user.id)

			utag9obj = Recipe.objects.filter(tag__icontains='Vegetable').filter(rating__user_id=request.user.id)
			utag9avg = utag9obj.aggregate(Avg('rating__rating'))
			print(utag9avg)
			utag9 = int(round(utag9avg['rating__rating__avg'], 0))
			print(utag9)




		elif 'matrix' in request.POST:

			start = datetime.now()

			uobj = User.objects.exclude(id=1)

			for u in uobj:
				rtstr = ""
				for x in range(1, 1141, 1):
					if Rating.objects.filter(user_id=u.id).filter(recipe_id=x).exists():
						rtobj = Rating.objects.filter(user_id=u.id).filter(recipe_id=x).get()
						urating = rtobj.rating
					else:
						urating = 0

					if rtstr == "":
						rtstr = str(urating)
					else:
						tstr = "@"+str(urating)
						rtstr = rtstr+tstr

				print("User: ", u.id, "\n", rtstr)
				new = Matrix(user_id=u.id, rating_list=rtstr)
				new.save()

			end = datetime.now()

			delta = end - start

			msgstr = "Execution Time: "+str(delta.seconds)+" seconds"

			messages.success(request, msgstr)
				

	return render(request, "recipes/recipe_manage.html", context)


def psort(v):

	out = v[1]

	return out	


def bin2dec(binary): 
      
    binary1 = binary 
    decimal, i, n = 0, 0, 0
    while(binary != 0): 
        dec = binary % 10
        decimal = decimal + dec * pow(2, i) 
        binary = binary//10
        i += 1

    return decimal


def Algorithm(request):

	cuser = request.user
	cuser_id = cuser.id

	'''

	# Overall Average Rating per tag

	otag1obj = Recipe.objects.filter(tag__icontains='Beef')
	otag1avg = otag1obj.aggregate(Avg('rating__rating'))
	# print(otag1avg)
	otag1 = int(round(otag1avg['rating__rating__avg'], 0))
	# print(otag1)

	otag2obj = Recipe.objects.filter(tag__icontains='Dessert')
	otag2avg = otag2obj.aggregate(Avg('rating__rating'))
	# print(otag2avg)
	otag2 = int(round(otag2avg['rating__rating__avg'], 0))
	# print(otag2)

	otag3obj = Recipe.objects.filter(tag__icontains='Fish')
	otag3avg = otag3obj.aggregate(Avg('rating__rating'))
	# print(otag3avg)
	otag3 = int(round(otag3avg['rating__rating__avg'], 0))
	# print(otag3)

	otag4obj = Recipe.objects.filter(tag__icontains='Noodle')
	otag4avg = otag4obj.aggregate(Avg('rating__rating'))
	# print(otag4avg)
	otag4 = int(round(otag4avg['rating__rating__avg'], 0))
	# print(otag4)

	otag5obj = Recipe.objects.filter(tag__icontains='Pork')
	otag5avg = otag5obj.aggregate(Avg('rating__rating'))
	# print(otag5avg)
	otag5 = int(round(otag5avg['rating__rating__avg'], 0))
	# print(otag5)

	otag6obj = Recipe.objects.filter(tag__icontains='Poultry')
	otag6avg = otag6obj.aggregate(Avg('rating__rating'))
	# print(otag6avg)
	otag6 = int(round(otag6avg['rating__rating__avg'], 0))
	# print(otag6)

	otag7obj = Recipe.objects.filter(tag__icontains='Rice')
	otag7avg = otag7obj.aggregate(Avg('rating__rating'))
	# print(otag7avg)
	otag7 = int(round(otag7avg['rating__rating__avg'], 0))
	# print(otag7)

	otag8obj = Recipe.objects.filter(tag__icontains='Seafood')
	otag8avg = otag8obj.aggregate(Avg('rating__rating'))
	# print(otag8avg)
	otag8 = int(round(otag8avg['rating__rating__avg'], 0))
	# print(otag8)

	otag9obj = Recipe.objects.filter(tag__icontains='Vegetable')
	otag9avg = otag9obj.aggregate(Avg('rating__rating'))
	# print(otag9avg)
	otag9 = int(round(otag9avg['rating__rating__avg'], 0))
	# print(otag9)

	'''

	# Current User Average Rating per tag

	utag1obj = Recipe.objects.filter(tag__icontains='Beef').filter(rating__user_id=cuser_id)
	if utag1obj.count() == 0:
		utag1 = 0
	else:
		utag1avg = utag1obj.aggregate(Avg('rating__rating'))
		# print(utag1avg)
		utag1 = int(round(utag1avg['rating__rating__avg'], 0))
		# print(utag1)

	utag2obj = Recipe.objects.filter(tag__icontains='Dessert').filter(rating__user_id=cuser_id)
	if utag2obj.count() == 0:
		utag2 = 0
	else:
		utag2avg = utag2obj.aggregate(Avg('rating__rating'))
		# print(utag2avg)
		utag2 = int(round(utag2avg['rating__rating__avg'], 0))
		# print(utag2)

	utag3obj = Recipe.objects.filter(tag__icontains='Fish').filter(rating__user_id=cuser_id)
	if utag3obj.count() == 0:
		utag3 = 0
	else:
		utag3avg = utag3obj.aggregate(Avg('rating__rating'))
		# print(utag3avg)
		utag3 = int(round(utag3avg['rating__rating__avg'], 0))
		# print(utag3)

	utag4obj = Recipe.objects.filter(tag__icontains='Noodle').filter(rating__user_id=cuser_id)
	if utag4obj.count() == 0:
		utag4 = 0
	else:
		utag4avg = utag4obj.aggregate(Avg('rating__rating'))
		# print(utag4avg)
		utag4 = int(round(utag4avg['rating__rating__avg'], 0))
		# print(utag4)

	utag5obj = Recipe.objects.filter(tag__icontains='Pork').filter(rating__user_id=cuser_id)
	if utag5obj.count() == 0:
		utag5 = 0
	else:
		utag5avg = utag5obj.aggregate(Avg('rating__rating'))
		# print(utag5avg)
		utag5 = int(round(utag5avg['rating__rating__avg'], 0))
		# print(utag5)

	utag6obj = Recipe.objects.filter(tag__icontains='Poultry').filter(rating__user_id=cuser_id)
	if utag6obj.count() == 0:
		utag6 = 0
	else:
		utag6avg = utag6obj.aggregate(Avg('rating__rating'))
		# print(utag6avg)
		utag6 = int(round(utag6avg['rating__rating__avg'], 0))
		# print(utag6)

	utag7obj = Recipe.objects.filter(tag__icontains='Rice').filter(rating__user_id=cuser_id)
	if utag7obj.count() == 0:
		utag7 = 0
	else:
		utag7avg = utag7obj.aggregate(Avg('rating__rating'))
		# print(utag7avg)
		utag7 = int(round(utag7avg['rating__rating__avg'], 0))
		# print(utag7)

	utag8obj = Recipe.objects.filter(tag__icontains='Seafood').filter(rating__user_id=cuser_id)
	if utag8obj.count() == 0:
		utag8 = 0
	else:
		utag8avg = utag8obj.aggregate(Avg('rating__rating'))
		# print(utag8avg)
		utag8 = int(round(utag8avg['rating__rating__avg'], 0))
		# print(utag8)

	utag9obj = Recipe.objects.filter(tag__icontains='Vegetable').filter(rating__user_id=cuser_id)
	if utag9obj.count() == 0:
		utag9 = 0
	else:
		utag9avg = utag9obj.aggregate(Avg('rating__rating'))
		# print(utag9avg)
		utag9 = int(round(utag9avg['rating__rating__avg'], 0))
		# print(utag9)


	
	# current user rating list
	cuser_list = np.array([])
	ty = np.array([])


	for i in range(1, 1141):
		lenul = len(cuser_list)
		robj = Recipe.objects.get(id=i)
		tag = str(robj.tag)
		# print(tag)

		if '@' in tag:
			ttag = tag.split('@')
			tag = ttag[0]
			# print(tag)

		if Rating.objects.filter(user_id=cuser_id).filter(recipe_id=i).exists():
			rateobj = Rating.objects.filter(user_id=cuser_id).filter(recipe_id=i).get()
			urate = int(rateobj.rating)
			# print(urate)
		else:
			urate = 0

		# new input 1
		if Recipe.objects.filter(id=i).exists():
			rcrtobj = Rating.objects.filter(recipe_id=i)
			if rcrtobj.count() == 0:
				inp1 = 0
			else:
				rcrtavg = rcrtobj.aggregate(Avg('rating'))
				inp1 = int(round(rcrtavg['rating__avg'], 0))

		if tag == 'Beef':
			# inp1 = otag1
			inp2 = utag1
		elif tag == 'Dessert':
			# inp1 = otag2
			inp2 = utag2
		elif tag == 'Fish':
			# inp1 = otag3
			inp2 = utag3
		elif tag == 'Noodle':
			# inp1 = otag4
			inp2 = utag4
		elif tag == 'Pork':
			# inp1 = otag5
			inp2 = utag5
		elif tag == 'Poultry':
			# inp1 = otag6
			inp2 = utag6
		elif tag == 'Rice':
			# inp1 = otag7
			inp2 = utag7
		elif tag == 'Seafood':
			# inp1 = otag8
			inp2 = utag8
		elif tag == 'Vegetable':
			# inp1 = otag9
			inp2 = utag9

		generated_list = np.array([inp1, inp2, tag, urate])
		yval = urate

		if lenul == 0:
			cuser_list = generated_list
			ty = np.array([yval])
		else:
			cuser_list = np.vstack((cuser_list, generated_list))
			ty = np.append(ty, yval)
		


	converted_list = cuser_list
	

	# ANN
	K.clear_session()

	BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

	list_len = len(converted_list[0])

	temp = np.array([])

	for c in range(list_len-1):
		# one hot encoding
		tcol = converted_list[:, c]
		tcolenc = LabelEncoder()
		tcolenc.fit(tcol)
		encoded_col = tcolenc.transform(tcol)
		col = to_categorical(encoded_col)
		# decimal to binary input 1 and 2
		if c == 0:
			temp = dec2bin(tcol)
		elif c < 2:
			temp = np.hstack((temp, dec2bin(tcol)))
		# tags and rate will use one hot encoding
		else:
			temp = np.hstack((temp, col))

	# temporary values where X is the input and y is the output
	X = temp

	

	y = ty

	model = load_model(os.path.join(BASE_DIR, 'assets/models/save_model'))

	# inverse one hot encoding to get the predicted data
	predictions = model.predict_classes(X)
	X_ = np.argmax(to_categorical(predictions), axis = 1)

	# if not yet numerical
	'''
	encoder = LabelEncoder()
	encoder.fit(X_)
	X_ = encoder.inverse_transform(X_)
	'''

	counter = 0

	cuser_list = []

	# Display ANN Prediction
	for i in X_:
		
		# input 1 overall
		inp1 = converted_list[counter][0]
		# input 2 current user
		inp2 = converted_list[counter][1]
		# input 3 tag
		inp3 = converted_list[counter][2]
		# expected output from unsliced data
		out = converted_list[counter][3]
		# predicted output
		# pre = int(i)+1
		pre = int(i)
		# expected output from sliced data
		exp = y[counter]
		# print(counter+1)
		# print("Input1: ", inp1, ", Input2: ", inp2, ", Tag: ", inp3, ", Predicted: ", pre, ", Expected: ", exp, ", Con:", out)
		# print("Input1: ", inp1, ", Input2: ", inp2, ", Tag: ", inp3, ", Predicted: ", pre)
		# print('Recipe_id:', counter+1)
		# if the user didn't rate it it'll use the predicted rating
		if exp == 0:
			# print('Input1:', inp1, '|Input2:', inp2, '|Input3:', inp3, '|Predicted:', pre)
			cuser_list.insert(counter, pre)
		else:
			# print('Rating by the current user:', exp)
			cuser_list.insert(counter, exp)

		# print('-----------------------------------------------------------')
		# insert to current user ratings
		# cuser_list.insert(counter, pre)
		counter += 1

	# print(cuser_list)


	# excluding current user and the superadmin
	ex_id = [cuser_id, 1]

	# ratings of all users
	ratingtb = dict()

	ratingtb[cuser_id] = cuser_list

	K.clear_session()


	# Matrix Factorization

	mobj = Matrix.objects.exclude(id__in=ex_id)

	for m in mobj:

		rtstr = m.rating_list
		temp_rating = rtstr.split("@")
		temp_rating = np.array(temp_rating).astype(int)

		ratingtb[m.user_id] = temp_rating


	# print(ratingtb)

	# Collaborative Filtering using pearson correlation coefficient

	user_index = cuser_id

	similarity_table = []

	for i in ratingtb:
		# print(i)
		# print(ratingtb[i])
		# if i != user_index:
		similarity = [i, pearsonr(ratingtb[i], ratingtb[user_index])[0]]
		similarity_table.append(similarity)

	similarity_table.sort(reverse=True, key=psort)
	# print('Current User ID:',cuser_id)
	# print('Similarity:')
	# print(similarity_table)
	reco_list = []

	# top 5 similar users
	for d in similarity_table:
		if len(reco_list) < 5:
			if d[0] != user_index:
				reco_list.append(d[0])
		else:
			break

	# print('Top 5 Most Similar Users to the Current User:')
	# print(reco_list)

	return reco_list


def Mass(value):

	unit = value

	out = False

	if 'kilogram' in unit.lower() or 'kg' in unit.lower():
		out = True
	elif 'gram' in unit.lower() or 'g' == unit.lower():
		out = True
	elif 'ounce' in unit.lower() or 'oz' in unit.lower():
		out = True
	elif 'pound' in unit.lower() or 'lb' in unit.lower():
		out = True

	return out


def Volume(value):

	unit = value

	out = False

	if 'cup' in unit.lower() or 'c' == unit.lower():
		out = True
	elif 'liter' in unit.lower() or 'l' == unit.lower():
		out = True
	elif 'mililiter' in unit.lower() or 'ml' in unit.lower():
		out = True
	elif 'quart' in unit.lower() or 'qt' == unit.lower():
		out = True
	elif 'tablespoon' in unit.lower() or 'tbsp' in unit.lower():
		out = True
	elif 'teaspoon' in unit.lower() or 'tsp' in unit.lower():
		out = True

	return out


def Others(value):

	unit = value

	out = False

	if 'big bottle' in unit.lower() or 'bb' == unit.lower():
		out = True
	elif 'bottle' in unit.lower() or 'b' == unit.lower():
		out = True
	elif 'bunch' in unit.lower() or 'bc' == unit.lower():
		out = True
	elif 'can' in unit.lower() or 'cn' == unit.lower():
		out = True
	elif 'clove' in unit.lower() or 'cv' == unit.lower():
		out = True
	elif 'head' in unit.lower() or 'h' == unit.lower():
		out = True
	elif 'package' in unit.lower() or 'pg' == unit.lower():
		out = True
	elif 'pack' in unit.lower() or 'p' == unit.lower():
		out = True
	elif 'piece' in unit.lower() or 'pc' == unit.lower():
		out = True
	elif 'pouch' in unit.lower() or 'po' == unit.lower():
		out = True
	elif 'stalk' in unit.lower() or 's' == unit.lower():
		out = True
	elif 'whole' in unit.lower() or 'w' == unit.lower():
		out = True

	return out


def Acro(value):

	unit = value

	if 'kilogram' in unit.lower() or 'kg' in unit.lower():
		out = 'kg'

	elif 'gram' in unit.lower():
		out = 'g'

	elif 'ounce' in unit.lower() or 'oz' in unit.lower():
		out = 'oz'

	elif 'pound' in unit.lower() or 'lb' in unit.lower():
		out = 'lb'

	elif 'cup' in unit.lower():
		out = 'c'

	elif 'liter' in unit.lower():
		out = 'l'

	elif 'mililiter' in unit.lower() or 'ml' in unit.lower():
		out = 'ml'

	elif 'quart' in unit.lower():
		out = 'qt'

	elif 'tablespoon' in unit.lower() or 'tbsp' in unit.lower():
		out = 'tbsp'

	elif 'teaspoon' in unit.lower() or 'tsp' in unit.lower():
		out = 'tsp'

	elif 'big bottle' in unit.lower():
		out = 'bb'

	elif 'bottle' in unit.lower():
		out = 'b'

	elif 'bunch' in unit.lower():
		out = 'bc'

	elif 'can' in unit.lower():
		out = 'cn'

	elif 'clove' in unit.lower():
		out = 'cv'

	elif 'head' in unit.lower():
		out = 'h'

	elif 'package' in unit.lower():
		out = 'pg'

	elif 'pack' in unit.lower():
		out = 'p'

	elif 'piece' in unit.lower():
		out = 'pc'

	elif 'pouch' in unit.lower():
		out = 'po'

	elif 'stalk' in unit.lower():
		out = 's'

	elif 'whole' in unit.lower():
		out = 'w'

	else:
		out = 'nothing'

	return out


def conMass(qty, aunit, ivunit):

	massl = {'g':1.0, 'kg':1000.0, 'oz':28.35, 'lb':454}

	out = qty*massl[aunit]/massl[ivunit]

	return out


def conVolume(qty, aunit, ivunit):

	volumel = {'ml':1.0, 'c':240, 'l':1000, 'qt':946, 'tbsp':14.787, 'tsp':4.929}

	# quantity * recipe unit / inventory unit
	out = qty*volumel[aunit]/volumel[ivunit]

	return out


def checkfrac(value):

	txt = value

	arr = []

	arr = re.findall(r"\d+\/\d+|\d+\s\d+\/\d+", txt)

	if len(arr) > 0:
		out = True
	else:
		out = False

	return out


def dec2frac(value):

	txt = round(value, 2)

	whole = frac(txt).limit_denominator(100)

	num = frac(txt).limit_denominator(100).numerator

	den = frac(txt).limit_denominator(100).denominator

	if num > den:
		whole = int(num/den)
		# print('Whole:',whole)
		num = num%den
		gcd = math.gcd(num, den)
		# print(gcd)
		# while gcd != 1:
		# print(gcd)
		num = int(num/gcd)
		den = int(den/gcd)

		out = '{} {}/{}'.format(whole, num, den)
		# print('Final:',out)
	 
	else:
		out = '{} {}/{}'.format(num, den)
		# print('Final:',out)	

	return out


def frac2dec(value):

	txt = value

	txt = txt.lstrip()
	txt = txt.rstrip()

	chk = []

	chk = re.findall(r"\d+\s\d+\/\d+", txt)

	# if mixed fraction
	if len(chk) > 0:
		
		arr = []

		arr = re.split(r"\s", txt)

		whole = float(arr[0])
		frac = arr[1]
		no = re.split(r"\/", frac)
		num = float(no[0])
		den = float(no[1])

		tdec = round(num/den, 2)

		out = whole+tdec


	else:
		
		arr = []

		arr = re.split(r"\/", txt)
		num = float(arr[0])
		den = float(arr[1])

		out = round(num/den, 2)


	return out


def pint(value):

	# parse int

	txt = value

	arr = []

	arr = re.findall(r"\d+", txt)

	if len(arr) > 0:
		out = arr[0]

	else:

		out = 1

	return out

