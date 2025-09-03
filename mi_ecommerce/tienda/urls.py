# tienda/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('producto/<int:id>/', views.detalle_producto, name='detalle_producto'),
]