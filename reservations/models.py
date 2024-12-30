from ast import arg
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

class Client(models.Model) :
    nom = models.CharField(max_length=255)
    nombre_adultes = models.PositiveIntegerField()
    nombre_enfants = models.PositiveIntegerField()
    duree_sejour =  models.PositiveIntegerField()
    budget = models.PositiveIntegerField()
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)


    def __str__(self):
        return f" Nom : {self.nom}, Budget :{self.budget}"
    
class Deplacement(models.Model) :
    nom = models.CharField(max_length=255)
    TYPE_CHOICES = [("voiture", "Voiture" ) , ('minibus', 'Minibus') , ("bus","Bus")]
    type = models.CharField(max_length=255,choices=TYPE_CHOICES)
    tarif_journalier = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
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
    tarif = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)


    class Meta:
        unique_together = ('hotel', 'numero')  # Contrainte d'unicité
        
    def __str__(self): 
        return f"{self.hotel.nom} : {self.numero} {self.type} : ({'Disponible' if self.disponibilite else 'Indisponible' })"
    
class Itineraire (models.Model) :
    nom = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='itineraires', null=True )
    description = models.TextField(blank = True, null=True)
    duree = models.PositiveIntegerField(help_text="Durée en jours")
    debut = models.DateField()
    fin = models.DateField()
    deplacement = models.ForeignKey(Deplacement, on_delete= models.CASCADE, related_name='itineraires', null=True)
    tarif = models.DecimalField(max_digits=10, decimal_places=2, blank = True, null=True) 
    payer = models.BooleanField(default= False)


    def __str__(self): 
        return f"Itineraire : {self.nom} "
    
    def calcule_tarif_totale(self) :
        nb_jours = (self.fin - self.debut).days + 1 
        tarif_deplacement = nb_jours * self.deplacement.tarif_journalier
        jours = self.jour_itineraire.all()
        tarif_jours = sum(jour.tarif or 0 for jour  in jours )
        self.tarif = tarif_jours + tarif_deplacement
        
        return self.tarif
    


    


class Activite(models.Model):
    nom = models.CharField(max_length=255)
    duree = models.PositiveIntegerField(help_text="Durée en minutes")
    nom_prestataire = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    photos = models.ImageField(upload_to='photos/activites/', blank=True, null=True)
    tarif = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)


    def __str__(self):
        return self.nom
    
class Jour(models.Model) :
    date = models.DateField()  
    activites = models.ManyToManyField(Activite, blank=True, related_name='jours') 
    itineraire = models.ForeignKey(Itineraire, on_delete=models.CASCADE, related_name='jour_itineraire', null=True)
    chambres = models.ManyToManyField(Chambre, blank=True, related_name='chambres') 
    tarif = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    

    def __str__(self):
        return f"le jour : {self.date}"
    
    def calculer_tarif_jour(self) :
        tarif_chambres = sum(chambre.tarif  or 0 for chambre in self.chambres.all())
        tarif_activites = sum(activite.tarif or 0 for activite in self.activites.all())
        self.tarif = tarif_chambres + tarif_activites

        return self.tarif
@receiver(m2m_changed, sender=Jour.chambres.through)
@receiver(m2m_changed, sender=Jour.activites.through)
def update_tarif_on_m2m_change(sender, instance, action, **kwargs):
    # Si l'action implique une mise à jour réelle des relations (ajout, suppression ou nettoyage)
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Recalculer le tarif et mettre à jour l'instance
        instance.tarif = instance.calculer_tarif_jour()
        instance.save()


# Signal pour mettre à jour le tarif de 'Itineraire' lorsqu'un 'deplacement' est modifié
@receiver(post_save, sender=Itineraire)
def update_tarif_on_deplacement_change(sender, instance, created, **kwargs):
    if instance.tarif is None or instance.tarif == 0:
        # Calculer le tarif uniquement si nécessaire
        instance.tarif = instance.calcule_tarif_totale()
        instance.save()

# Signal pour mettre à jour le tarif dans 'Jour' lors de la modification de l'itinéraire
@receiver(post_save, sender=Jour)
def update_jour_on_save(sender, instance, created, **kwargs):
    if not hasattr(instance, '_is_saving'):
        instance._is_saving = True
        # Calculer le tarif uniquement si nécessaire
        tarif_initial = instance.tarif
        instance.tarif = instance.calculer_tarif_jour()
        if instance.tarif != tarif_initial:
            instance.save()  # Ne sauvegarder que si le tarif a changé
        del instance._is_saving
    
