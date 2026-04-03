from django.urls import path
from . import views

urlpatterns = [
    path('', views.mouvement_liste, name='mouvement_liste'),
    path('nouveau/', views.mouvement_creer, name='mouvement_creer'),
]