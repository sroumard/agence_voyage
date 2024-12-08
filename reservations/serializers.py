from datetime import datetime
from rest_framework import serializers
from .models import Client, Itineraire, Hotel, Activite, Jour, Deplacement, ReservationHotel

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class ItineraireSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)

    class Meta:
        model = Itineraire
        fields = '__all__'

class HotelSerializer(serializers.ModelSerializer):
    chambres_disponibles = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = '__all__'

    def get_chambres_disponibles(self, obj):
        result = None  # Valeur par défaut si aucune donnée valide n'est fournie
        request = self.context.get('request')
    
        if request:
            debut = request.query_params.get('debut')
            fin = request.query_params.get('fin')
            
            if debut and fin:
                try:
                    debut_date = datetime.strptime(debut, "%Y-%m-%d").date()
                    fin_date = datetime.strptime(fin, "%Y-%m-%d").date()
                    result = obj.chambres_disponibles(debut_date, fin_date)
                except ValueError:
                    pass  # Laisse 'result' à sa valeur par défaut (None)
    
        return result


class ActiviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activite
        fields = '__all__'

class JourSerializer(serializers.ModelSerializer):
    hotel = HotelSerializer()
    activites = ActiviteSerializer(many=True)

    class Meta:
        model = Jour
        fields = '__all__'

class DeplacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deplacement
        fields = '__all__'

class ReservationHotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationHotel
        fields = '__all__'
