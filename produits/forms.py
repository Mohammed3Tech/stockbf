from django import forms
from .models import Produit, Categorie, Fournisseur


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = [
            'nom', 'description', 'categorie', 'fournisseur',
            'prix_achat', 'prix_vente', 'quantite',
            'seuil_alerte', 'image', 'code_barre'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du produit'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description du produit'
            }),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'prix_achat': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'prix_vente': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'seuil_alerte': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '5'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'code_barre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Code barre (optionnel)'
            }),
        }


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la catégorie'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'telephone', 'email', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du fournisseur'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+226 XX XX XX XX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Adresse complète'
            }),
        }