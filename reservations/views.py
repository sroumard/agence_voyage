from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect,HttpResponse
import requests
from .models import Client, Itineraire, Hotel, Activite, Jour, Deplacement
from .forms import ClientForm, DeplacementForm, ItineraireForm, UserRegistrationForm
from datetime import date, datetime
from rest_framework import viewsets, generics
from rest_framework.response import Response
from .serializers import ClientSerializer, ItineraireSerializer, HotelSerializer, ActiviteSerializer, JourSerializer, DeplacementSerializer
from django.contrib import messages
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.core.paginator import Paginator
def home(request):
    return render(request, 'reservations/home.html')

def register(request) :
    if request.method =="POST" :
        form = UserRegistrationForm(request.POST)
        if form.is_valid() :
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f' Count create for {username} ! Vous pouvez maintenant vous connecter.')
            return redirect("home")
    else : 
        form = UserRegistrationForm(request.POST)
    
    return render (request, "reservations/register.html", {"form" : form} )
         

class CustomLoginView(LoginView):
    template_name = 'reservations/login.html'  # Le template HTML à utiliser
    redirect_authenticated_user = True  # Redirige si l'utilisateur est déjà connecté
    next_page = reverse_lazy('dashboard')  # Redirige après connexion (remplacez 'home' par le nom de votre vue d'accueil)

@login_required
def logout_view(request):
    if request.method == "GET":
        logout(request)
        return redirect('home')  # Redirige vers la page de connexion après déconnexion

@login_required
def dashboard(request):
    return render(request, 'reservations/dashboard.html')


@login_required
def creer_deplacement(request) :
    if request.method == "POST" :
        form = DeplacementForm(request.POST)
        if form.is_valid() :
            form.save()
            return redirect('afficher_deplacements_page')
    else:
        form = DeplacementForm(request.POST)

    return render (request,'reservations/creer_deplacement.html', {'form' : form} )
@login_required
def creer_client(request) :
    if request.method == "POST" :
        form = ClientForm(request.POST)
        if form.is_valid() :
            form.save()
            return redirect('afficher_clients_page')
    else:
        form = ClientForm(request.POST)

    return render (request,'reservations/creer_client.html', {'form' : form} )



@login_required
def verifier_disponibilites(request):
    if request.method == "POST":
        debut = request.POST.get('debut')
        fin = request.POST.get('fin')

        try:
            debut_date = datetime.strptime(debut, "%Y-%m-%d").date()
            fin_date = datetime.strptime(fin, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "Dates invalides"}, status=400)

        hotels_disponibles = []
        for hotel in Hotel.objects.all():
            chambres_disponibles = hotel.chambres_disponibles(debut_date, fin_date)
            if chambres_disponibles > 0:
                hotels_disponibles.append({
                    "nom": hotel.nom,
                    "latitude": hotel.latitude,
                    "longitude": hotel.longitude,
                    "chambres_disponibles": chambres_disponibles
                })

        return JsonResponse({"hotels": hotels_disponibles})
    
    return render(request, 'reservations/verifier_disponibilites.html')


@login_required
def creer_itineraire(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == "POST" :
        form = ItineraireForm(request.POST)
        if form.is_valid():
            itineraire = form.save(commit=False)
            itineraire.client = client
            itineraire.save()
            return HttpResponseRedirect(f'/clients/{client_id}/itineraires/')
    else:
        form = ItineraireForm()
    return render(request, 'reservations/creer_itineraire.html', {'form': form, 'client': client})


@login_required
def finaliser_itineraire(request, itineraire_id):
    itineraire = get_object_or_404(Itineraire, id=itineraire_id)
    jours = itineraire.jours.all()
    total_budget = sum(jour.hotel.note * 100 for jour in jours)  # Exemple de calcul de coûts
    return render(request, 'reservations/finaliser_itineraire.html', {
        'itineraire': itineraire,
        'jours': jours,
        'total_budget': total_budget,
    })

@login_required
def gestion_transport(request, itineraire_id):
    itineraire = get_object_or_404(Itineraire, id=itineraire_id)
    transports_disponibles = Deplacement.objects.filter(itineraires=itineraire)
    return render(request, 'reservations/gestion_transport.html', {
        'itineraire': itineraire,
        'transports_disponibles': transports_disponibles,
    })

@login_required
def ajouter_hotels(request):
    # Définir la requête Overpass API pour récupérer les hôtels
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = """
    [out:json];
    node["tourism"="hotel"](-8.8,114.224199,-8.1,116.469920);  // Zone autour de bali
    out;
    """
    try:
        response = requests.get(overpass_url, params={'data': query})
        response.raise_for_status()  # Vérifie si la requête a réussi
        hotels = response.json().get("elements", [])
        nom_hotel = request.GET.get('nom',None)
        if nom_hotel:
            hotels = [hotel for hotel in hotels if nom_hotel.lower() in hotel.get('tags', {}).get('name', '').lower()]
# lower pour convertir en miniscule et tags c'est un mot clé dans l'api ducoup on filtre avec dictionnaire du dictionnaire
    except requests.RequestException as e:
        hotels = []  # En cas d'erreur, aucune donnée n'est renvoyée
        print(f"Erreur lors de la récupération des données : {e}")
    
    # Passer les données au template
    return render(request, 'reservations/ajouter_hotel.html', {'hotels': hotels})

@login_required
def afficher_hotels(request) : 
    search_query = request.GET.get('search', '')
    hotels = Hotel.objects.filter(nom__icontains=search_query)  # Filtrer les hotels par nom
    paginator = Paginator(hotels, 10)  # Pagination avec 10 hotels par page
    page_number = request.GET.get('page')  # Numéro de page
    page_obj = paginator.get_page(page_number)  # Récupérer la page


    # Définir la requête Overpass API pour récupérer les hôtels
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = """
    [out:json];
    node["tourism"="hotel"](-8.8,114.224199,-8.1,116.469920);  // Zone autour de bali
    out;
    """
    try:
        response = requests.get(overpass_url, params={'data': query})
        response.raise_for_status()  # Vérifie si la requête a réussi
        hotels_map = response.json().get("elements", [])
        nom_hotel = request.GET.get('nom',None)
        if nom_hotel:
            hotels_map = [hotel for hotel in hotels_map if nom_hotel.lower() in hotel.get('tags', {}).get('name', '').lower()]
# lower pour convertir en miniscule et tags c'est un mot clé dans l'api ducoup on filtre avec dictionnaire du dictionnaire
    except requests.RequestException as e:
        hotels_map = []  # En cas d'erreur, aucune donnée n'est renvoyée
        print(f"Erreur lors de la récupération des données : {e}")
    
    # Passer les données au template
    return render(request,'reservations/afficher_hotels.html',{
        "hotels": page_obj, 
        "search_query": search_query,
        'hotels_map': hotels_map
        })

def modifier_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('afficher_clients_page')
    else:
        form = ClientForm(instance=client)
    return render(request, 'reservations/modifier_client.html', {'form': form})

def modifier_deplacement(request, deplacement_id):
    deplacement = get_object_or_404(Deplacement, id=deplacement_id)

    if request.method == 'POST':
        form = DeplacementForm(request.POST, instance=deplacement)
        if form.is_valid():
            form.save()
            return redirect('afficher_deplacements_page')
    else:
        form = DeplacementForm(instance=deplacement)
    return render(request, 'reservations/modifier_deplacement.html', {'form': form})

def supprimer_client(request, client_id) :
    if request.method == "DELETE" :    
        client = get_object_or_404(Client, id = client_id)
        client.delete()
        messages.success(request, 'Client deleted successfully.')
        return redirect('dashboard')
    return render(request, 'reservations/supprimer_client.html')

def supprimer_deplacement(request, deplacement_id) :
    if request.method == "DELETE" :    
        deplacement = get_object_or_404(Deplacement, id = deplacement_id)
        deplacement.delete()
        messages.success(request, 'Transport deleted successfully.')
        return redirect('dashboard')
    return render(request, 'reservations/supprimer_deplacement.html')

def afficher_deplacements(request) : 
    search_query = request.GET.get('search', '')
    deplacements = Deplacement.objects.filter(nom__icontains=search_query)  # Filtrer les deplacements par nom
    paginator = Paginator(deplacements, 10)  # Pagination avec 10 clients par page
    page_number = request.GET.get('page',1)  # Numéro de page
    page_obj = paginator.get_page(page_number)  # Récupérer la page

    # Convertir les clients en JSON
    deplacements_data = [
        {
            "id": deplacement.id,
            "name": deplacement.nom,
            "type": deplacement.type,
            "price": deplacement.tarif_journalier,
            "capacity": deplacement.capacite,
    
        } for deplacement in page_obj
    ]

    return JsonResponse({
        "deplacements" : deplacements_data,
        "has_previous" : page_obj.has_previous(),
        "has_next" : page_obj.has_next(),
        "current_page" : page_obj.number,
        "num_pages" : paginator.num_pages,
    })
def afficher_clients(request):
    search_query = request.GET.get('search', '')
    clients = Client.objects.filter(nom__icontains=search_query)  # Filtrer les clients par nom
    paginator = Paginator(clients, 10)  # Pagination avec 10 clients par page
    page_number = request.GET.get('page',1)  # Numéro de page
    page_obj = paginator.get_page(page_number)  # Récupérer la page

    # Convertir les clients en JSON
    clients_data = [
        {
            "id": client.id,
            "nom": client.nom,
            "nombre_adultes": client.nombre_adultes,
            "nombre_enfants": client.nombre_enfants,
            "duree_sejour": client.duree_sejour,
            "budget": client.budget,
            "email": client.email,
        } for client in page_obj
    ]

    return JsonResponse({
        "clients" : clients_data,
        "has_previous" : page_obj.has_previous(),
        "has_next" : page_obj.has_next(),
        "current_page" : page_obj.number,
        "num_pages" : paginator.num_pages,
    })

def afficher_clients_page(request):
    return render(request, 'reservations/afficher_clients.html')

def afficher_deplacements_page(request):
    return render(request, 'reservations/afficher_deplacements.html')
 
def afficher_itineraires(request): 
    search_query = request.GET.get('search', '')
    itineraires = Itineraire.objects.filter(nom__icontains=search_query)
    paginator = Paginator(itineraires, 10)  # Pagination avec 10 clients par page
    page_number = request.GET.get('page')  # Numéro de page
    page_obj = paginator.get_page(page_number)  # Récupérer la page
    itineraires_data = [
        {
            "id": itineraire.id,
            "nom": itineraire.nom,
            "customer": itineraire.client.nom,
            "duration": itineraire.duree,
            "begin": itineraire.debut,
            "end": itineraire.fin,
            "price": itineraire.tarif,
            "payer": itineraire.payer,
        } for itineraire in page_obj
    ]

    return JsonResponse({
        "itineraires" : itineraires_data,
        "has_previous" : page_obj.has_previous(),
        "has_next" : page_obj.has_next(),
        "current_page" : page_obj.number,
        "num_pages" : paginator.num_pages,
    })

def afficher_itineraires_page(request):
    return render(request, 'reservations/afficher_itineraires.html')  


# cette fonction remplace creer et modifier
@login_required
def gerer_client(request, client_id=None):
    client = get_object_or_404(Client, id=client_id) if client_id else None
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('afficher_clients_page')
    else:
        form = ClientForm(instance=client)
    return render(request, 'reservations/gerer_client.html', {'form': form})

@login_required
def gerer_deplacement(request, deplacement_id=None):
    deplacement = get_object_or_404(Deplacement, id=deplacement_id) if deplacement_id else None
    if request.method == "POST":
        form = DeplacementForm(request.POST, instance=deplacement)
        if form.is_valid():
            form.save()
            return redirect('afficher_deplacements_page')
    else:
        form = DeplacementForm(instance=deplacement)
    return render(request, 'reservations/gerer_deplacement.html', {'form': form})

@login_required
def gerer_itineraire(request, itineraire_id=None):
    itineraire = get_object_or_404(Itineraire, id=itineraire_id) if itineraire_id else None
    if request.method == "POST":
        form = ItineraireForm(request.POST, instance=itineraire)
        if form.is_valid():
            form.save()
            return redirect('afficher_itineraires_page')
    else:
        form = ItineraireForm(instance=itineraire)
    return render(request, 'reservations/gerer_itineraire.html', {'form': form})













def enregistrer_hotel(request):
    if request.method == "POST":
        nom = request.POST.get('nom')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        description = request.POST.get('description')

        # Enregistrer dans la base de données
        Hotel.objects.create(
            nom=nom,
            latitude=latitude,
            longitude=longitude,
        )

        return HttpResponse(status=204)





def generer_facture_PDF(request, itineraire_id):
    # Récupérer l'itinéraire
    itineraire = get_object_or_404(Itineraire, id=itineraire_id)
    
    # Récupérer les détails de l'itinéraire
    details = []
    for jour in itineraire.jour_itineraire.all():
        hotels = [chambre.hotel.nom for chambre in jour.chambres.all()]

        activites = [activite.nom for activite in jour.activites.all()]
        details.append({
            "jour": jour.date,
            "hotel": hotels[0],
            "activites": activites
        })
    
    # Créer une réponse HTTP avec un fichier PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Ajouter le titre de la facture
    p.setFont("Helvetica", 16)
    p.drawString(100, 750, f"Facture pour l'itinéraire: {itineraire.nom}")
    
    # Informations de transport
    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Transport: {itineraire.deplacement}")

    # Détails par jour
    y_position = 710
    p.drawString(100, y_position, "Détails par jour:")
    y_position -= 20
    
    for jour_details in details:
        jour_str = f"{jour_details['jour']} - Hôtel: {jour_details['hotel']}"
        p.drawString(100, y_position, jour_str)
        y_position -= 15
        
        if jour_details['activites']:
            activites_str = f"Activités: {', '.join(jour_details['activites'])}"
            p.drawString(120, y_position, activites_str)
            y_position -= 15
    
    # Prix total
    y_position -= 20
    p.drawString(100, y_position, f"Prix total: {itineraire.tarif}€")
    
    # Finaliser le PDF
    p.showPage()
    p.save()
    
    # Revenir au début du fichier et envoyer la réponse
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{itineraire.nom}.pdf"'
    return response


# vues serailisé 
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class ItineraireViewSet(viewsets.ModelViewSet) :
    queryset = Itineraire.objects.all()
    serializer_class = ItineraireSerializer

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

class ActiviteViewSet(viewsets.ModelViewSet):
    queryset = Activite.objects.all()
    serializer_class = ActiviteSerializer

class JourViewSet(viewsets.ModelViewSet):
    queryset = Jour.objects.all()
    serializer_class = JourSerializer

class DeplacementViewSet(viewsets.ModelViewSet):
    queryset = Deplacement.objects.all()
    serializer_class = DeplacementSerializer





# gerer paiement avec strip

# views.py
import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Deplacement

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request, itineraire_id):
    itineraire = get_object_or_404(Itineraire, id=itineraire_id)
    if request.method == 'POST':
        try:
            # Créer une session de paiement
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': itineraire.nom,
                        },
                        'unit_amount': int(itineraire.tarif*(1.1)),  # + 10% de tva
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/success/'),
                cancel_url=request.build_absolute_uri('/cancel/'),
            )
            return JsonResponse({'id': session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return render(request, 'reservations/checkout.html', {'itineraire': itineraire, 'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY})

def payment_success(request):
    return render(request, 'reservations/payment_success.html')

def payment_cancel(request):
    return render(request, 'reservations/payment_cancel.html')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Itineraire

@csrf_exempt
def toggle_payment(request, itineraire_id):
    itineraire = get_object_or_404(Itineraire, id=itineraire_id)
    itineraire.payer = not itineraire.payer
    itineraire.save()
    return JsonResponse({"success": True, "payer": itineraire.payer})


