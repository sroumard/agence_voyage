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

    path('afficher_clients/', views.afficher_clients_page, name='afficher_clients_page'),
    path('afficher_deplacements/', views.afficher_deplacements_page, name='afficher_deplacements_page'),
    path('afficher_itineraires/', views.afficher_itineraires_page, name='afficher_itineraires_page'),


    path('gerer_client/', views.gerer_client, name='gerer_client'),
    path('gerer_client/<int:client_id>/', views.gerer_client, name='gerer_client'),
    path('gerer_deplacement/', views.gerer_deplacement, name='gerer_deplacement'),
    path('gerer_deplacement/<int:deplacement_id>/', views.gerer_deplacement, name='gerer_deplacement'),
    path('modifier_deplacement/<int:deplacement_id>/', views.modifier_deplacement, name='modifier_deplacement'),

    path('api/clients/<int:client_id>/delete', views.supprimer_client, name='supprimer_client'),
    path('api/deplacements/<int:deplacement_id>/delete', views.supprimer_deplacement, name='supprimer_deplacement'),


    path('creer_deplacement/', views.creer_deplacement, name='creer_deplacement'),
    path('clients/<int:client_id>/creer_itineraire/', views.creer_itineraire, name='creer_itineraire'),
    path('itineraires/<int:itineraire_id>/finaliser/', views.finaliser_itineraire, name='finaliser_itineraire'),
    path('itineraires/<int:itineraire_id>/transport/', views.gestion_transport, name='gestion_transport'),
    path('ajouter_hotels/', views.ajouter_hotels, name='ajouter_hotels'),
    path('enregistrer_hotel/', views.enregistrer_hotel, name='enregistrer_hotel'),  # Nouveau chemin
    path('facture/<int:itineraire_id>/', views.generer_facture_PDF, name='generer_facture'),

    path('api/clients/', views.afficher_clients, name='afficher_clients'),
    path('api/deplacements/', views.afficher_deplacements, name='afficher_deplacements'),
    path('api/itineraires/', views.afficher_itineraires, name='afficher_itineraires'),

    path('api/', include(router.urls)),  # API Rest

 # payment
    path('checkout/<int:itineraire_id>/', views.checkout, name='checkout'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),

    path('api/itineraires/<int:itineraire_id>/toggle_payment', views.toggle_payment, name='toggle_payment'),

]
