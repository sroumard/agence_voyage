from django import forms
from .models import Client, Itineraire, Jour, Deplacement, Hotel


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = "__all__"
        


class ItineraireForm(forms.ModelForm):
    class Meta:
        model = Itineraire
        fields = '__all__'


class JourForm(forms.ModelForm):
    class Meta:
        model = Jour
        fields = '__all__'

class DeplacementForm(forms.ModelForm):
    class Meta:
        model = Deplacement
        fields = '__all__'

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = '__all__'