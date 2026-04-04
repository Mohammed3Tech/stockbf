import re

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from django.contrib.auth.models import User


class InscriptionForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}
    ))
    first_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Prénom'}
    ))
    last_name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Nom'}
    ))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Ali123'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[\w\d@.+\-_]+$', username):
            raise forms.ValidationError(
                "Le nom d'utilisateur ne peut contenir que des lettres, chiffres et @/./+/-/_"
        )
        return username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmer mot de passe'
        })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name or user.username} !')
            return redirect('dashboard')
        else:
            messages.error(request, 'Identifiants incorrects.')
    else:
        form = AuthenticationForm()
    form.fields['username'].widget = forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nom utilisateur'
    })
    form.fields['password'].widget = forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Mot de passe'
    })
    return render(request, 'comptes/login.html', {'form': form})


def inscription_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Compte créé ! Bienvenue {user.first_name} !')
            return redirect('dashboard')
    else:
        form = InscriptionForm()
    return render(request, 'comptes/inscription.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('login')


@login_required
def profil_view(request):
    return render(request, 'comptes/profil.html', {'user': request.user})