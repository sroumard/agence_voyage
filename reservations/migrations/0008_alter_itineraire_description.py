# Generated by Django 5.1.1 on 2024-12-15 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0007_remove_itineraire_prix_alter_itineraire_tarif'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itineraire',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
