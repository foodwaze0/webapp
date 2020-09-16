"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views

# static files
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from recipes.views import RecipeListView, AboutView, JargonView, ManageView, Search, BeefView, DessertView, FishView, NoodleView, PorkView, PoultryView, RiceView, SeafoodView, VegetableView, RecommendList
from accounts.views import RegisterView, LoginView, Logout, ResList, ResUpdate, ResRemove
from inventories.views import RecommendView

urlpatterns = [
	path('recipes/', include('recipes.urls')),
	path('home/', RecipeListView.as_view(), name='home'),
    path('inventory/', include('inventories.urls')),
    path('jargon/', JargonView, name='jargon'),
    path('about/', AboutView, name='about'),
    path('login/', LoginView, name='login'),
    path('logout/', Logout, name='logout'),
    path('register/', RegisterView, name='register'),
    path('restriction/', ResList, name='restriction'),
    path('restriction/update/', ResUpdate, name='restriction-update'),
    path('restriction/remove/', ResRemove, name='restriction-remove'),
    path('manage/', ManageView, name='manage'), 
    path('admin/', admin.site.urls),
    path('search/', Search, name='search'),
    path('beef/', BeefView, name='beef'),
    path('dessert/', DessertView, name='dessert'),
    path('fish/', FishView, name='fish'),
    path('noodle/', NoodleView, name='noodle'),
    path('pork/', PorkView, name='pork'),
    path('poultry/', PoultryView, name='poultry'),
    path('rice/', RiceView, name='rice'),
    path('seafood/', SeafoodView, name='seafood'),
    path('vegetable/', VegetableView, name='vegetable'),
    path('recommend/', RecommendView, name='recommend'),
    path('recommend/list/', RecommendList, name='recommend-list'),

    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),

    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),

    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'), name='password_reset'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),


]

urlpatterns += staticfiles_urlpatterns()