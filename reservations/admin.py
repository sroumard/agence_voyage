from django.contrib import admin
from .models import Client, Itineraire, Hotel, Deplacement, Activite, Chambre, Jour
# Enregistrer les modèles dans l'administration



admin.site.register(Client)
admin.site.register(Itineraire)
admin.site.register(Hotel)
admin.site.register(Deplacement)
admin.site.register(Activite)
admin.site.register(Chambre)
admin.site.register(Jour)

