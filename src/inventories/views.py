from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect	

from django.core.paginator import Paginator

from .models import Inventory
from .forms import InventoryModelForm, AddInventoryForm
from recipes.models import Ingredient

# Create your views here.

# Object Mixin to reduce redundancy
class InventoryObjectMixin(object):
	model = Inventory
	lookup = 'id'

	def get_object(self):
		id = self.kwargs.get('id')
		obj = None
		if id is not None:
			obj = get_object_or_404(self.model, id=id)
		return obj


class InventoryListView(LoginRequiredMixin, View):
	login_url = '/login/'
	template_name = "inventories/inventory_list.html"


	def get_query(self):
		return Inventory.objects.filter(username=self.request.user)

	def get(self, request, *args, **kwargs):
		paginator = Paginator(self.get_query(), 10)
		page = request.GET.get('page')
		inventories = paginator.get_page(page)
		context = {'inventories': inventories}
		return render(request, self.template_name, context)

	def post(self, request, id=None, *args, **kwargs):
		data = request.POST.dict()
		did = data.get("id")
		obj = Inventory.objects.filter(id=did)
		obj.delete()
		return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))


class InventoryView(LoginRequiredMixin, InventoryObjectMixin, View):

	login_url = '/login/'

	template_name = "inventories/inventory_detail.html"

	def check_user(self):
		username = str(self.request.user)
		other = str(self.get_object().username)
		if username == other:
			return True
		else:
			return False


	def get(self, request, id=None, *args, **kwargs): 

		if self.check_user() == False:
			raise PermissionDenied()
		else:
			context = {}
			obj = self.get_object()
			if obj is not None:
				# form = InventoryModelForm(instance=obj)

				ingrobj = Ingredient.objects.all()

				ingrl = []

				for i in ingrobj:
					name = i.name
					name = name.lstrip()
					name = name.rstrip()
					if name not in ingrl:
						ingrl.append(name)

				ingrl.sort()

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

				form = InventoryModelForm()
				form.fields['ingr'].initial = obj.ingr
				form.fields['qty'].initial = obj.qty
				form.fields['unit'].choices = UNIT_CHOICES
				form.fields['unit'].initial = obj.unit
				'''
				if obj.unit.lower() in 'kilogram':
					form.fields['unit'].initial = 'kilogram'
				else:
					form.fields['unit'].initial = 'liter'
				
				context['object'] = obj
				context['form'] = form
				'''
				context = {
					'object': obj,
					'form': form,
					'ingrl': ingrl,
				}

			return render(request, self.template_name, context)

	def post(self, request, id=None, *args, **kwargs):
		context = {}
		obj = self.get_object()
		if obj is not None:

			ingrobj = Ingredient.objects.all()

			ingrl = []

			for i in ingrobj:
				name = i.name
				name = name.lstrip()
				name = name.rstrip()
				if name not in ingrl:
					ingrl.append(name)

			ingrl.sort()

			form = InventoryModelForm(request.POST, instance=obj)
			if form.is_valid():
				form.save()
				return redirect('/inventory/')
			
			'''	
			context['object'] = obj
			context['form'] = form
			'''

			context = {
				'object': obj,
				'form': form,
				'ingrl': ingrl,
			}

		return render(request, self.template_name, context)


class InventoryCreateView(LoginRequiredMixin, View):
	login_url = '/login/'
	template_name = "inventories/inventory_list.html"

	template_name = "inventories/inventory_create.html"
	def get(self, request, *args, **kwargs):
		form = AddInventoryForm() 
		ingrobj = Ingredient.objects.all()

		ingrl = []

		for i in ingrobj:
			name = i.name
			name = name.lstrip()
			name = name.rstrip()
			if name not in ingrl:
				ingrl.append(name)

		ingrl.sort()

		context = {
				"form": form,
				"ingrl": ingrl,
				}
		return render(request, self.template_name, context)


	def post(self, request, *args, **kwargs): 
		form = AddInventoryForm(request.POST)
		if form.is_valid():
			form.instance.username = self.request.user
			form.save()
			form = AddInventoryForm()
			return redirect('/inventory/')

		context = {"form": form}
		return render(request, self.template_name, context)


def RecommendView(request, *args, **kwargs):

	if request.user.is_authenticated:
		invobj = Inventory.objects.filter(username=request.user)

	context = {
		'inventories': invobj,
	}	

	return render(request, "inventories/recommend.html", context)