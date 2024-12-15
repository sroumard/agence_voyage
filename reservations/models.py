from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Client(models.Model) :
    nom = models.CharField(max_length=255)
    nombre_adultes = models.PositiveIntegerField()
    nombre_enfants = models.PositiveIntegerField()
    duree_sejour =  models.PositiveIntegerField()
    budget = models.PositiveIntegerField()
    email = models.EmailField(max_length=255, unique=True)


    def __str__(self):
        return f" Nom : {self.nom}, Budget :{self.budget}"
    
class Deplacement(models.Model) :
    nom = models.CharField(max_length=255)
    TYPE_CHOICES = [("voiture", "Voiture" ) , ('minibus', 'Minibus') , ("bus","Bus")]
    type = models.CharField(max_length=255,choices=TYPE_CHOICES)
    tarif_journalier = models.FloatField()
    capacite = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.nom}"
    
class Hotel(models.Model):
    nom = models.CharField(max_length=255)
    photos = models.ImageField(upload_to='photos/hotels/', blank=True, null=True)
    description = models.TextField(null=True, blank= True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    note = models.DecimalField(
    max_digits=3,
    decimal_places=1,
    validators=[MinValueValidator(0), MaxValueValidator(5)],
    help_text="La note doit être comprise entre 0 et 5.",
    null=True,  # Permet d'enregistrer NULL dans la base de données
    blank=True  # Permet de ne pas remplir ce champ dans les formulaires
    )
   
    total_chambres = models.PositiveIntegerField(help_text="Nombre total de chambres dans l'hôtel.",null=True, blank= True)

    def __str__(self):
        return self.nom
    
    
class Chambre(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="chambres")
    numero = models.PositiveIntegerField()
    type = models.CharField(max_length=255,choices=[("single","Single"),("double","Double")])
    disponibilite = models.BooleanField(default= True)

    class Meta:
        unique_together = ('hotel', 'numero')  # Contrainte d'unicité
        
    def __str__(self): 
        return f"num : {self.numero} est :({'Disponible' if self.disponibilite else 'Indisponible' })"
    
class Itineraire (models.Model) :
    nom = models.CharField(max_length=255)
    prix = models.PositiveIntegerField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='itineraires', null=True )
    description = models.TextField()
    duree = models.PositiveIntegerField(help_text="Durée en jours")
    debut = models.DateField()
    fin = models.DateField()
    deplacement = models.ForeignKey(Deplacement, on_delete= models.CASCADE, related_name='itineraires', null=True)

class Activite(models.Model):
    nom = models.CharField(max_length=255)
    duree = models.PositiveIntegerField(help_text="Durée en minutes")
    nom_prestataire = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    photos = models.ImageField(upload_to='photos/activites/', blank=True, null=True)

    def __str__(self):
        return self.nom
    
class Jour(models.Model) :
    date = models.DateField()  
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name ="Hotel")
    activite = models.ManyToManyField(Activite, blank=True, related_name='jours') 
    itineraire = models.ForeignKey(Itineraire, on_delete=models.CASCADE, related_name='jours', null=True)
    
    def __str__(self):
        return f"le jour : {self.date}"
    
class Facture(models.Model) :
    Itineraire = models.ForeignKey(Itineraire, on_delete=models.CASCADE,related_name="Itineraire")
    client = models.ForeignKey(Client, on_delete = models.CASCADE, related_name = "Facture")
    jours = models.ManyToManyField(Jour)
    prix_total = models.DecimalField(blank=True, null=True)
    
    def __str__(self):
        return f"Facture de {self.client}"
    
#details l'itinieraire et activités pour chaque jour 

    def get_details_Jours(self):
        details = []
        activites= []
        for jour in self.jours.all() :
            hotel = jour.hotel
            for activite in jour.activite.all() :
                activites.append(activite.nom)
            
            details.append({
                'date' : jour.date,
                'hotel' : hotel.nom,
                'activites' : activites,
                })
        return details
        

    
    


