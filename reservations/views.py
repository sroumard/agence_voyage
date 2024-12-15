from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from .models import Client, Itineraire, Hotel, Activite, Jour, Deplacement
from .forms import ClientForm, ItineraireForm
from datetime import date, datetime
from rest_framework import viewsets, generics
from rest_framework.response import Response
from .serializers import ClientSerializer, ItineraireSerializer, HotelSerializer, ActiviteSerializer, JourSerializer, DeplacementSerializer




def creer_client(request) :
    if request.method == "POST" :
        form = ClientForm(request.POST)
        if form.is_valid() :
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = ClientForm(request.POST)

    return render (request,'reservations/creer_client.html', {'form' : form} )




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


def ajouter_jour_itineraire(request, itineraire_id):
    itineraire = get_object_or_404(Itineraire, id=itineraire_id)
    if request.method == "POST":
        form = JourForm(request.POST)
        if form.is_valid():
            jour = form.save(commit=False)
            jour.itineraire = itineraire
            jour.save()
            form.save_m2m()
            return HttpResponseRedirect(f'/itineraires/{itineraire_id}/')
    else:
        form = JourForm()
    return render(request, 'reservations/ajouter_jour_itineraire.html', {'form': form, 'itineraire': itineraire})

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

def afficher_hotel(request):
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
    return render(request, 'reservations/afficher_hotel.html', {'hotels': hotels})



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
"""
def generer_facture(request, itineraire_id):
    itineraire = get_object_or_404(Itineraire,id=itineraire_id)
    details = []
    for jour in itineraire.jours :
        hotel = jour.hotel.nom
        activites = [activite.nom for activite in jour.activites.all()]
        details.append ({
            "jour": jour.id,
            "hotel" : hotel ,
            "activites" : activites}
            )

    # details= Facture.get_details_Jours(itineraire.jours)

    return {"itineraire": itineraire.nom, "transport": itineraire.deplacement ,"details par jours" : details}

"""
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