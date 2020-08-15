from django.urls import path
from .views import (
	InventoryListView,
	InventoryView,
	InventoryCreateView,
)

app_name = 'inventories'
urlpatterns = [
	
	path('', InventoryListView.as_view(), name='inventory-list'),
	path('create/', InventoryCreateView.as_view(), name='inventory-create'),
	path('<int:id>/', InventoryView.as_view(), name='inventory-detail'),

]