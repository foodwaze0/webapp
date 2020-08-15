from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
# put @login_required(login_url='login') above the page which will require login

from django.contrib import messages

# Create your views here.
from .forms import CreateUserForm, AddRestrictionForm

from .models import Restriction

def RegisterView(request):
	# if the user is authenticated
	if request.user.is_authenticated:
		return redirect('home')
	else:
		form = CreateUserForm()

		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				user = form.cleaned_data.get('username')
				messages.success(request, user+" has been registered!")
				return redirect('login')
			else:
				messages.error(request, "Error")

		context = {'form':form}
		return render(request, "accounts/register.html", context)


def LoginView(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(request, username=username, password=password)
			
			if user is not None:
				login(request, user)
				return redirect('home')
			else:
				messages.error(request, 'Incorrect Username or Password')
		context = {}
		return render(request, "accounts/login.html", context)

@login_required(login_url='login')
def Logout(request):
	logout(request)
	return redirect('login')

@login_required(login_url='login')
def ResList(request):
	obj = Restriction.objects.filter(username=request.user)
	rform = AddRestrictionForm()
	paginator = Paginator(obj, 5)
	page = request.GET.get('page')
	restrictions = paginator.get_page(page)
	if request.method == 'POST':
		if 'create' in request.POST:
			rform = AddRestrictionForm(request.POST or None)
			if rform.is_valid():
				rform.instance.username = request.user
				rform.save()
				rform = AddRestrictionForm()
				return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		elif 'restrict' in request.POST:
			username = request.user
			Restriction.objects.filter(username=username).update(check=True)
		elif 'disable' in request.POST:
			username = request.user
			Restriction.objects.filter(username=username).update(check=False)
	
	context = {
			"rform": rform,
			"obj": obj,
			"restrictions": restrictions,
			}
	return render(request, "accounts/restriction.html", context)

def ResUpdate(request):
	data = request.POST.dict()
	id = data.get("id")
	username = str(request.user)
	obj = Restriction.objects.get(id=id)
	ousername = str(obj.username)
	if username == ousername:
		tcheck = obj.check
		if tcheck == True:
			obj.check = False
			obj.save()
		else: 
			obj.check = True
			obj.save()
	else:
		raise PermissionDenied()

	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def ResRemove(request):
	data = request.POST.dict()
	id = data.get("id")
	username = str(request.user)
	obj = Restriction.objects.get(id=id)
	ousername = str(obj.username)
	if username == ousername:
		obj.delete()
	else:
		raise PermissionDenied()

	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))