from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import Mouvement
from produits.models import Produit


class MouvementForm(forms.ModelForm):
    class Meta:
        model = Mouvement
        fields = ['produit', 'type_mouvement', 'quantite', 'motif']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-select'}),
            'type_mouvement': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quantité',
                'min': 1
            }),
            'motif': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Motif du mouvement (optionnel)'
            }),
        }


@login_required
def mouvement_liste(request):
    mouvements = Mouvement.objects.select_related(
        'produit', 'created_by'
    ).all()[:50]
    return render(request, 'mouvements/liste.html', {
        'mouvements': mouvements
    })


@login_required
def mouvement_creer(request):
    produit_id = request.GET.get('produit')
    initial = {}
    if produit_id:
        initial['produit'] = produit_id

    if request.method == 'POST':
        form = MouvementForm(request.POST)
        if form.is_valid():
            mouvement = form.save(commit=False)
            mouvement.created_by = request.user

            # Vérification stock suffisant pour sortie
            if mouvement.type_mouvement == 'sortie':
                if mouvement.quantite > mouvement.produit.quantite:
                    messages.error(request,
                        f'Stock insuffisant ! Stock actuel : {mouvement.produit.quantite}'
                    )
                    return render(request, 'mouvements/form.html', {'form': form})

            mouvement.save()
            messages.success(request,
                f'Mouvement enregistré pour "{mouvement.produit.nom}"'
            )
            return redirect('mouvement_liste')
    else:
        form = MouvementForm(initial=initial)

    return render(request, 'mouvements/form.html', {'form': form})