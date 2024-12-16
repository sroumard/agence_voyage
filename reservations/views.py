from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect,HttpResponse
from .models import Client, Itineraire, Hotel, Activite, Jour, Deplacement
from .forms import ClientForm, ItineraireForm, UserRegistrationForm
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
    next_page = reverse_lazy('home')  # Redirige après connexion (remplacez 'home' par le nom de votre vue d'accueil)


def logout_view(request):
    if request.method == "GET":
        logout(request)
        return redirect('home')  # Redirige vers la page de connexion après déconnexion

def dashboard(request):
    return render(request, 'dashboard.html')
"""
def dashboard(request) :
    if request.method =="GET":
        hotels = Hotel.get_object_or_404.all()
        deplacements = Deplacement.get_object_or_404.all()
        clients = Client.get_object_or_404.all()
        itineraires = Itineraire.get_object_or_404.all()

        data= {
            "hotels" : hotels,
            "deplacements" : deplacements,
            "clients" : clients,
            "itineraires" : itineraires
        }
    return render(request,'reservations/dashboard.html',data)

"""


def creer_client(request) :
    if request.method == "POST" :
        form = ClientForm(request.POST)
        if form.is_valid() :
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = ClientForm(request.POST)

    return render (request,'creer_client.html', {'form' : form} )




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




def creer_itineraire(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == "POST":
        form = ItineraireForm(request.POST)
        if form.is_valid():
            itineraire = form.save(commit=False)
            itineraire.client = client
            itineraire.save()
            return HttpResponseRedirect(f'/clients/{client_id}/itineraires/')
    else:
        form = ItineraireForm()
    return render(request, 'reservations/creer_itineraire.html', {'form': form, 'client': client})



def finaliser_itineraire(request, itineraire_id):
    itineraire = get_object_or_404(Itineraire, id=itineraire_id)
    jours = itineraire.jours.all()
    total_budget = sum(jour.hotel.note * 100 for jour in jours)  # Exemple de calcul de coûts
    return render(request, 'reservations/finaliser_itineraire.html', {
        'itineraire': itineraire,
        'jours': jours,
        'total_budget': total_budget,
    })

def gestion_transport(request, itineraire_id):
    itineraire = get_object_or_404(Itineraire, id=itineraire_id)
    transports_disponibles = Deplacement.objects.filter(itineraires=itineraire)
    return render(request, 'reservations/gestion_transport.html', {
        'itineraire': itineraire,
        'transports_disponibles': transports_disponibles,
    })

import requests

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
    return render(request, 'reservations/ajouter_hotels.html', {'hotels': hotels})


def afficher_hotels(request) : 
    if request.method =="GET":
        hotels = Hotel.get_object_or_404.all()
    return render(request,'reservations/afficher_hotels.html',{"Hotels" :hotels})

def afficher_deplacements(request) : 
    if request.method =="GET":
        deplacements = Deplacement.get_object_or_404.all()
    return render(request,'reservations/afficher_deplacements.html',{"Transport" :deplacements})

def afficher_clients(request):
    if request.method =="GET":
        clients = Client.get_object_or_404.all()
    return render(request,'reservations/afficher_clients.html',{"Customers" : clients})
def afficher_itineraires(request): 
    if request.method =="GET":
        itineraires = Itineraire.get_object_or_404.all()
    return render(request,'reservations/afficher_itineraires.html',{"Hotels" : itineraires})   















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

        return redirect('afficher_hotel')  # Redirige vers la carte après l'enregistrement



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