from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('produits/', views.produit_liste, name='produit_liste'),
    path('produits/nouveau/', views.produit_creer, name='produit_creer'),
    path('produits/<int:pk>/', views.produit_detail, name='produit_detail'),
    path('produits/<int:pk>/modifier/', views.produit_modifier, name='produit_modifier'),
    path('produits/<int:pk>/supprimer/', views.produit_supprimer, name='produit_supprimer'),
    path('produits/export-csv/', views.export_csv, name='export_csv'),
    path('categories/', views.categorie_liste, name='categorie_liste'),
    path('categories/nouvelle/', views.categorie_creer, name='categorie_creer'),
    path('fournisseurs/', views.fournisseur_liste, name='fournisseur_liste'),
    path('fournisseurs/nouveau/', views.fournisseur_creer, name='fournisseur_creer'),
    path('produits/export-pdf/', views.export_pdf, name='export_pdf'),
    path('prevision/', views.prevision, name='prevision'),
]