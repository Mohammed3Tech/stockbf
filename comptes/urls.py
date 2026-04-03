from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('inscription/', views.inscription_view, name='inscription'),
    path('logout/', views.logout_view, name='logout'),
    path('profil/', views.profil_view, name='profil'),
]