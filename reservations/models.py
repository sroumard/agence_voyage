from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Client(models.Model):
    nom = models.CharField(max_length=255)
    nombre_adultes = models.PositiveIntegerField()
    nombre_enfants = models.PositiveIntegerField()
    duree_sejour = models.PositiveIntegerField(help_text="Durée en jours")
    budget = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nom} - {self.nombre_adultes} adultes, {self.nombre_enfants} enfants"


class Itineraire(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField()
    duree = models.PositiveIntegerField(help_text="Durée en jours")
    debut = models.DateField()
    fin = models.DateField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='itineraires', null=True)

    def __str__(self):
        return f"Itinéraire {self.nom} pour {self.client.nom}"


class Hotel(models.Model):
    nom = models.CharField(max_length=255)
    photos = models.ImageField(upload_to='photos/hotels/', blank=True, null=True)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    note = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="La note doit être comprise entre 0 et 5."
    )
    itineraires = models.ManyToManyField(Itineraire, related_name='hotels', blank=True)
    total_chambres = models.PositiveIntegerField(help_text="Nombre total de chambres dans l'hôtel.")

    def __str__(self):
        return self.nom
    def chambres_disponibles(self, debut, fin):
        """
        Calcule le nombre de chambres disponibles pour une période donnée.
        """
        reservations = self.reservations.filter(debut__lt=fin, fin__gt=debut)  # Réservations qui chevauchent la période
        chambres_occupees = sum(reservation.nombre_chambres for reservation in reservations)
        return self.total_chambres - chambres_occupees

class ReservationHotel(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="reservations")
    debut = models.DateField()
    fin = models.DateField()
    nombre_chambres = models.PositiveIntegerField()

    def __str__(self):
        return f"Réservation pour {self.hotel.nom} du {self.debut} au {self.fin}"
 

class Activite(models.Model):
    nom = models.CharField(max_length=255)
    duree = models.PositiveIntegerField(help_text="Durée en minutes")
    nom_prestataire = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    photos = models.ImageField(upload_to='photos/activites/', blank=True, null=True)

    def __str__(self):
        return self.nom


class Jour(models.Model):
    debut = models.DateField()
    fin = models.DateField()
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='jours')
    activites = models.ManyToManyField(Activite, blank=True, related_name='jours')
    itineraire = models.ForeignKey(Itineraire, on_delete=models.CASCADE, related_name='jours', null=True)

    def __str__(self):
        return f"Jour du {self.debut} au {self.fin} à {self.hotel.nom}"


class Deplacement(models.Model):
    nom = models.CharField(max_length=255)
    TYPE_CHOICES = [
        ('voiture', 'Voiture'),
        ('minibus', 'Minibus'),
        ('bus', 'Bus'),
    ]
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    tarif_par_jour = models.DecimalField(max_digits=10, decimal_places=2)
    capacite = models.PositiveIntegerField()
    itineraires = models.ManyToManyField(Itineraire, related_name='deplacements', blank=True)

    def __str__(self):
        return f"{self.type} - Capacité : {self.capacite}"
