from django.db import models
from django.contrib.auth.models import User
from produits.models import Produit


class Mouvement(models.Model):
    ENTREE = 'entree'
    SORTIE = 'sortie'
    AJUSTEMENT = 'ajustement'

    TYPE_CHOICES = [
        (ENTREE, 'Entrée de stock'),
        (SORTIE, 'Sortie de stock'),
        (AJUSTEMENT, 'Ajustement'),
    ]

    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name='mouvements'
    )
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantite = models.IntegerField()
    quantite_avant = models.IntegerField(default=0)
    quantite_apres = models.IntegerField(default=0)
    motif = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='mouvements'
    )

    class Meta:
        verbose_name = "Mouvement"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type_mouvement} - {self.produit.nom} ({self.quantite})"

    def save(self, *args, **kwargs):
        produit = self.produit
        self.quantite_avant = produit.quantite

        if self.type_mouvement == self.ENTREE:
            produit.quantite += self.quantite
        elif self.type_mouvement == self.SORTIE:
            produit.quantite -= self.quantite
        elif self.type_mouvement == self.AJUSTEMENT:
            produit.quantite = self.quantite

        self.quantite_apres = produit.quantite
        produit.save()
        super().save(*args, **kwargs)