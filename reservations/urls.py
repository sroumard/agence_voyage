from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'clients', views.ClientViewSet)
router.register(r'itineraires', views.ItineraireViewSet)
router.register(r'hotels', views.HotelViewSet)
router.register(r'activites', views.ActiviteViewSet)
router.register(r'jours', views.JourViewSet)
router.register(r'deplacements', views.DeplacementViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.verifier_disponibilites, name='verifier_disponibilites'),
    path('creer-client/', views.creer_client, name='creer_client'),
    path('clients/<int:client_id>/creer-itineraire/', views.creer_itineraire, name='creer_itineraire'),
    path('itineraires/<int:itineraire_id>/ajouter-jour/', views.ajouter_jour_itineraire, name='ajouter_jour_itineraire'),
    path('itineraires/<int:itineraire_id>/finaliser/', views.finaliser_itineraire, name='finaliser_itineraire'),
    path('itineraires/<int:itineraire_id>/transport/', views.gestion_transport, name='gestion_transport'),
    path('api/', include(router.urls)),  # API Rest
]
