# mon_app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClientViewSet, ItineraireViewSet, HotelViewSet,
    ActiviteViewSet, JourViewSet, DeplacementViewSet
)

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'itineraires', ItineraireViewSet)
router.register(r'hotels', HotelViewSet)
router.register(r'activites', ActiviteViewSet)
router.register(r'jours', JourViewSet)
router.register(r'deplacements', DeplacementViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
