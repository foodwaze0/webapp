from django.urls import path
from .views import (
	RecipeListView,
	RecipeView,
)

app_name = 'recipes'
urlpatterns = [
	
	# path('create/', CourseCreateView.as_view(), name='courses-create'),
	# path('<int:id>/update/', CourseUpdateView.as_view(), name='courses-update'),
	path('', RecipeListView.as_view(), name='recipe-list'),
	path('<slug:Title_link>/', RecipeView.as_view(), name='recipe-detail'),
	

	# path('', my_fbv, name='courses-list'),
]