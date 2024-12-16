# Generated by Django 5.1.1 on 2024-12-15 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0010_alter_activite_tarif'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jour',
            name='hotel',
        ),
        migrations.AddField(
            model_name='jour',
            name='chambres',
            field=models.ManyToManyField(blank=True, related_name='chambres', to='reservations.chambre'),
        ),
    ]