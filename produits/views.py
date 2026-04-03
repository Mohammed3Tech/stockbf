import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q, Sum
from .models import Produit, Categorie, Fournisseur
from .forms import ProduitForm, CategorieForm, FournisseurForm
from mouvements.models import Mouvement


@login_required
def dashboard(request):
    produits = Produit.objects.all()
    total_produits = produits.count()
    produits_alerte = produits.filter(quantite__lte=5)
    nb_alertes = produits_alerte.count()
    valeur_totale = sum(p.valeur_stock for p in produits)
    categories = Categorie.objects.all().count()
    derniers_mouvements = Mouvement.objects.select_related(
        'produit', 'created_by'
    )[:8]

    context = {
        'total_produits': total_produits,
        'nb_alertes': nb_alertes,
        'valeur_totale': valeur_totale,
        'categories': categories,
        'produits_alerte': produits_alerte,
        'derniers_mouvements': derniers_mouvements,
        'produits': produits,
    }
    return render(request, 'dashboard.html', context)


@login_required
def produit_liste(request):
    query = request.GET.get('q', '')
    categorie_id = request.GET.get('categorie', '')
    produits = Produit.objects.select_related('categorie', 'fournisseur')

    if query:
        produits = produits.filter(
            Q(nom__icontains=query) |
            Q(description__icontains=query) |
            Q(code_barre__icontains=query)
        )
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)

    categories = Categorie.objects.all()
    context = {
        'produits': produits,
        'categories': categories,
        'query': query,
        'categorie_selectionnee': categorie_id,
    }
    return render(request, 'produits/liste.html', context)


@login_required
def produit_detail(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    mouvements = produit.mouvements.select_related('created_by')[:10]
    return render(request, 'produits/detail.html', {
        'produit': produit,
        'mouvements': mouvements
    })


@login_required
def produit_creer(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.created_by = request.user
            produit.save()
            messages.success(request, f'Produit "{produit.nom}" créé avec succès !')
            return redirect('produit_liste')
    else:
        form = ProduitForm()
    return render(request, 'produits/form.html', {
        'form': form,
        'titre': 'Ajouter un produit',
        'btn': 'Enregistrer'
    })


@login_required
def produit_modifier(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, f'Produit "{produit.nom}" modifié avec succès !')
            return redirect('produit_liste')
    else:
        form = ProduitForm(instance=produit)
    return render(request, 'produits/form.html', {
        'form': form,
        'titre': f'Modifier — {produit.nom}',
        'btn': 'Mettre à jour'
    })


@login_required
def produit_supprimer(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        nom = produit.nom
        produit.delete()
        messages.success(request, f'Produit "{nom}" supprimé.')
        return redirect('produit_liste')
    return render(request, 'produits/confirmer_suppression.html', {
        'produit': produit
    })


@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stock_burkina.csv"'
    response.write('\ufeff')  # BOM pour Excel

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Nom', 'Catégorie', 'Fournisseur',
        'Prix Achat (FCFA)', 'Prix Vente (FCFA)',
        'Quantité', 'Seuil Alerte', 'Valeur Stock (FCFA)', 'Statut'
    ])

    for p in Produit.objects.select_related('categorie', 'fournisseur'):
        writer.writerow([
            p.nom,
            p.categorie.nom if p.categorie else '-',
            p.fournisseur.nom if p.fournisseur else '-',
            p.prix_achat,
            p.prix_vente,
            p.quantite,
            p.seuil_alerte,
            p.valeur_stock,
            '⚠️ ALERTE' if p.est_en_alerte else '✅ OK'
        ])

    return response


@login_required
def categorie_liste(request):
    categories = Categorie.objects.all()
    return render(request, 'produits/categories.html', {'categories': categories})


@login_required
def categorie_creer(request):
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Catégorie créée avec succès !')
            return redirect('categorie_liste')
    else:
        form = CategorieForm()
    return render(request, 'produits/form_categorie.html', {
        'form': form, 'titre': 'Nouvelle catégorie'
    })


@login_required
def fournisseur_liste(request):
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'produits/fournisseurs.html', {
        'fournisseurs': fournisseurs
    })


@login_required
def fournisseur_creer(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fournisseur ajouté avec succès !')
            return redirect('fournisseur_liste')
    else:
        form = FournisseurForm()
    return render(request, 'produits/form_fournisseur.html', {
        'form': form, 'titre': 'Nouveau fournisseur'
    })

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime


@login_required
def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport_stock_burkina.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=1.5*cm
    )

    elements = []
    styles = getSampleStyleSheet()

    # Couleurs
    VIOLET = colors.HexColor('#667eea')
    ROUGE = colors.HexColor('#e94560')
    GRIS_CLAIR = colors.HexColor('#f8f9fa')
    GRIS = colors.HexColor('#6c757d')
    VERT = colors.HexColor('#28a745')
    ORANGE = colors.HexColor('#ffc107')

    # Style titre principal
    style_titre = ParagraphStyle(
        'titre',
        parent=styles['Title'],
        fontSize=22,
        textColor=VIOLET,
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    style_sous_titre = ParagraphStyle(
        'sous_titre',
        parent=styles['Normal'],
        fontSize=11,
        textColor=GRIS,
        spaceAfter=2,
        alignment=TA_CENTER,
    )

    style_section = ParagraphStyle(
        'section',
        parent=styles['Normal'],
        fontSize=13,
        textColor=VIOLET,
        spaceBefore=16,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )

    style_normal = ParagraphStyle(
        'normal',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#333333'),
    )

    style_alerte = ParagraphStyle(
        'alerte',
        parent=styles['Normal'],
        fontSize=9,
        textColor=ROUGE,
        fontName='Helvetica-Bold'
    )

    # ── ENTÊTE ──
    elements.append(Paragraph("🇧🇫 StockBF", style_titre))
    elements.append(Paragraph("Rapport de Gestion de Stock — Burkina Faso", style_sous_titre))
    elements.append(Paragraph(
        f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} par {request.user.get_full_name() or request.user.username}",
        style_sous_titre
    ))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=VIOLET))
    elements.append(Spacer(1, 0.4*cm))

    # ── KPI SUMMARY ──
    produits = Produit.objects.select_related('categorie', 'fournisseur').all()
    total_produits = produits.count()
    produits_alerte = produits.filter(quantite__lte=5)
    nb_alertes = produits_alerte.count()
    valeur_totale = sum(p.valeur_stock for p in produits)
    nb_categories = Categorie.objects.count()

    kpi_data = [
        ['TOTAL PRODUITS', 'ALERTES STOCK', 'VALEUR TOTALE', 'CATÉGORIES'],
        [
            str(total_produits),
            str(nb_alertes),
            f"{valeur_totale:,.0f} FCFA",
            str(nb_categories)
        ]
    ]

    kpi_table = Table(kpi_data, colWidths=[4.5*cm, 4.5*cm, 5.5*cm, 4*cm])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), VIOLET),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWHEIGHT', (0,0), (-1,0), 20),
        ('ROWHEIGHT', (0,1), (-1,1), 28),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (-1,1), 14),
        ('TEXTCOLOR', (0,1), (0,1), VIOLET),
        ('TEXTCOLOR', (1,1), (1,1), ROUGE),
        ('TEXTCOLOR', (2,1), (2,1), VERT),
        ('TEXTCOLOR', (3,1), (3,1), colors.HexColor('#17a2b8')),
        ('BACKGROUND', (0,1), (-1,1), GRIS_CLAIR),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 0.5*cm))

    # ── TABLEAU COMPLET DES PRODUITS ──
    elements.append(Paragraph("📦 Inventaire Complet des Produits", style_section))

    headers = ['#', 'Produit', 'Catégorie', 'Fournisseur', 'P. Achat', 'P. Vente', 'Qté', 'Valeur', 'Statut']
    data = [headers]

    for i, p in enumerate(produits.order_by('categorie__nom', 'nom'), 1):
        statut = '⚠ ALERTE' if p.est_en_alerte else '✓ OK'
        data.append([
            str(i),
            p.nom[:28],
            p.categorie.nom if p.categorie else '—',
            p.fournisseur.nom[:15] if p.fournisseur else '—',
            f"{p.prix_achat:,.0f}",
            f"{p.prix_vente:,.0f}",
            str(p.quantite),
            f"{p.valeur_stock:,.0f}",
            statut
        ])

    col_widths = [0.7*cm, 4.5*cm, 2.8*cm, 3*cm, 2.2*cm, 2.2*cm, 1.2*cm, 2.5*cm, 1.8*cm]
    produits_table = Table(data, colWidths=col_widths, repeatRows=1)

    style_table = TableStyle([
        # Header
        ('BACKGROUND', (0,0), (-1,0), VIOLET),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ROWHEIGHT', (0,0), (-1,0), 18),
        # Body
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('ALIGN', (0,1), (0,-1), 'CENTER'),
        ('ALIGN', (4,1), (7,-1), 'RIGHT'),
        ('ALIGN', (6,1), (6,-1), 'CENTER'),
        ('ALIGN', (8,1), (8,-1), 'CENTER'),
        ('ROWHEIGHT', (0,1), (-1,-1), 16),
        ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#dee2e6')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ])

    # Lignes alternées + alertes
    for i in range(1, len(data)):
        p_obj = list(produits.order_by('categorie__nom', 'nom'))[i-1]
        if p_obj.est_en_alerte:
            style_table.add('BACKGROUND', (0,i), (-1,i), colors.HexColor('#fff3cd'))
            style_table.add('TEXTCOLOR', (8,i), (8,i), ROUGE)
            style_table.add('FONTNAME', (8,i), (8,i), 'Helvetica-Bold')
        elif i % 2 == 0:
            style_table.add('BACKGROUND', (0,i), (-1,i), GRIS_CLAIR)

    produits_table.setStyle(style_table)
    elements.append(produits_table)
    elements.append(Spacer(1, 0.5*cm))

    # ── PRODUITS EN ALERTE ──
    if nb_alertes > 0:
        elements.append(Paragraph("⚠️ Produits Nécessitant un Réapprovisionnement Urgent", style_section))

        alerte_data = [['Produit', 'Catégorie', 'Stock actuel', 'Seuil alerte', 'À commander']]
        for p in produits_alerte:
            a_commander = max(p.seuil_alerte * 3 - p.quantite, 0)
            alerte_data.append([
                p.nom,
                p.categorie.nom if p.categorie else '—',
                str(p.quantite),
                str(p.seuil_alerte),
                f"{a_commander} unités"
            ])

        alerte_table = Table(alerte_data, colWidths=[5*cm, 3.5*cm, 3*cm, 3*cm, 4*cm])
        alerte_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), ROUGE),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (2,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#dee2e6')),
            ('ROWHEIGHT', (0,0), (-1,-1), 18),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#fff3cd')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#856404')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(alerte_table)
        elements.append(Spacer(1, 0.5*cm))

    # ── HISTORIQUE MOUVEMENTS ──
    elements.append(Paragraph("📋 Historique des Derniers Mouvements", style_section))

    mouvements = Mouvement.objects.select_related('produit', 'created_by').all()[:20]
    mouv_data = [['Produit', 'Type', 'Avant', 'Qté', 'Après', 'Motif', 'Par', 'Date']]

    for m in mouvements:
        type_label = 'Entrée' if m.type_mouvement == 'entree' else ('Sortie' if m.type_mouvement == 'sortie' else 'Ajust.')
        mouv_data.append([
            m.produit.nom[:20],
            type_label,
            str(m.quantite_avant),
            str(m.quantite),
            str(m.quantite_apres),
            m.motif[:20] if m.motif else '—',
            m.created_by.username if m.created_by else '—',
            m.created_at.strftime('%d/%m/%Y')
        ])

    mouv_table = Table(mouv_data, colWidths=[3.5*cm, 1.8*cm, 1.5*cm, 1.2*cm, 1.5*cm, 3.5*cm, 2.2*cm, 2.2*cm])
    mouv_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#343a40')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#dee2e6')),
        ('ROWHEIGHT', (0,0), (-1,-1), 16),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ])

    for i in range(1, len(mouv_data)):
        if i % 2 == 0:
            mouv_style.add('BACKGROUND', (0,i), (-1,i), GRIS_CLAIR)
        m_obj = list(mouvements)[i-1]
        if m_obj.type_mouvement == 'entree':
            mouv_style.add('TEXTCOLOR', (1,i), (1,i), VERT)
        elif m_obj.type_mouvement == 'sortie':
            mouv_style.add('TEXTCOLOR', (1,i), (1,i), ROUGE)

    mouv_table.setStyle(mouv_style)
    elements.append(mouv_table)
    elements.append(Spacer(1, 0.5*cm))

    # ── PIED DE PAGE ──
    elements.append(HRFlowable(width="100%", thickness=1, color=VIOLET))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        f"StockBF — Solution de gestion de stock pour le Burkina Faso | "
        f"NATAMA Mohammed & SAWADOGO Bachirou | {datetime.now().strftime('%Y')}",
        ParagraphStyle('footer', parent=styles['Normal'],
            fontSize=7, textColor=GRIS, alignment=TA_CENTER)
    ))

    doc.build(elements)
    return 


@login_required
def prevision(request):
    produits = Produit.objects.prefetch_related('mouvements').all()
    previsions = []

    for p in produits:
        # Calcul consommation moyenne sur les 30 derniers jours
        from django.utils import timezone
        from datetime import timedelta

        date_limite = timezone.now() - timedelta(days=30)
        sorties = p.mouvements.filter(
            type_mouvement='sortie',
            created_at__gte=date_limite
        )
        total_sorties = sum(m.quantite for m in sorties)
        nb_jours = 30
        conso_journaliere = round(total_sorties / nb_jours, 2)
        conso_hebdo = round(conso_journaliere * 7, 1)

        # Jours restants avant rupture
        if conso_journaliere > 0:
            jours_restants = int(p.quantite / conso_journaliere)
        else:
            jours_restants = 999

        # Quantité à commander (stock 60 jours)
        stock_cible = int(conso_journaliere * 60)
        a_commander = max(stock_cible - p.quantite, 0)

        # Niveau de risque
        if jours_restants <= 7:
            risque = 'critique'
        elif jours_restants <= 15:
            risque = 'eleve'
        elif jours_restants <= 30:
            risque = 'moyen'
        else:
            risque = 'ok'

        previsions.append({
            'produit': p,
            'conso_journaliere': conso_journaliere,
            'conso_hebdo': conso_hebdo,
            'jours_restants': jours_restants,
            'a_commander': a_commander,
            'risque': risque,
            'stock_cible': stock_cible,
        })

    # Trier par risque — critiques en premier
    ordre_risque = {'critique': 0, 'eleve': 1, 'moyen': 2, 'ok': 3}
    previsions.sort(key=lambda x: ordre_risque[x['risque']])

    # Comptage par risque
    nb_critique = sum(1 for p in previsions if p['risque'] == 'critique')
    nb_eleve = sum(1 for p in previsions if p['risque'] == 'eleve')
    nb_moyen = sum(1 for p in previsions if p['risque'] == 'moyen')
    nb_ok = sum(1 for p in previsions if p['risque'] == 'ok')

    return render(request, 'produits/prevision.html', {
        'previsions': previsions,
        'nb_critique': nb_critique,
        'nb_eleve': nb_eleve,
        'nb_moyen': nb_moyen,
        'nb_ok': nb_ok,
    })