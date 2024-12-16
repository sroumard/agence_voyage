from django import forms
from .models import Client, Itineraire, Jour, Deplacement, Hotel, Activite
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = "__all__"
        


class ItineraireForm(forms.ModelForm):
    class Meta:
        model = Itineraire
        fields = '__all__'




class DeplacementForm(forms.ModelForm):
    class Meta:
        model = Deplacement
        fields = '__all__'

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = '__all__'