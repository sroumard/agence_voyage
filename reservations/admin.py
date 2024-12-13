from django.contrib import admin
from .models import Client, Itineraire, Hotel, Deplacement, ReservationHotel, Activite
# Enregistrer les modèles dans l'administration
admin.site.register(Client)
admin.site.register(Itineraire)
admin.site.register(Hotel)
admin.site.register(Deplacement)
admin.site.register(ReservationHotel)
admin.site.register(Activite)