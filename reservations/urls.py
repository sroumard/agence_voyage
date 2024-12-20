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
    path('', views.home, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('afficher_hotels/', views.afficher_hotels, name='afficher_hotels'),
    path('afficher_deplacements/', views.afficher_deplacements, name='afficher_deplacements'),
    path('afficher_itineraires/', views.afficher_itineraires, name='afficher_itineraires'),
    path('afficher_clients/', views.afficher_clients_page, name='afficher_clients_page'),


    path('creer_client/', views.creer_client, name='creer_client'),
    path('clients/<int:client_id>/creer_itineraire/', views.creer_itineraire, name='creer_itineraire'),
    path('itineraires/<int:itineraire_id>/finaliser/', views.finaliser_itineraire, name='finaliser_itineraire'),
    path('itineraires/<int:itineraire_id>/transport/', views.gestion_transport, name='gestion_transport'),
    path('ajouter_hotels/', views.ajouter_hotels, name='ajouter_hotels'),
    path('enregistrer_hotel/', views.enregistrer_hotel, name='enregistrer_hotel'),  # Nouveau chemin
    path('facture/<int:itineraire_id>/', views.generer_facture_PDF, name='generer_facture'),

    path('api/clients/', views.afficher_clients, name='afficher_clients'),
    path('api/', include(router.urls)),  # API Rest
]
