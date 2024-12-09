from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from .models import Client, Itineraire, Hotel, Activite, Jour, Deplacement
from .forms import ClientForm, ItineraireForm, JourForm
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