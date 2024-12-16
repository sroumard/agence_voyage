# Generated by Django 5.1.1 on 2024-12-15 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0005_client_email_facture'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jour',
            old_name='activite',
            new_name='activites',
        ),
        migrations.AddField(
            model_name='activite',
            name='tarif',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True),
        ),
        migrations.AddField(
            model_name='chambre',
            name='tarif',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='itineraire',
            name='tarif',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.DeleteModel(
            name='Facture',
        ),
    ]