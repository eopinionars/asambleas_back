# Generated by Django 3.0 on 2020-05-27 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0011_pregunta_bloquea_mora'),
    ]

    operations = [
        migrations.AddField(
            model_name='preguntamultiple',
            name='strictMax',
            field=models.BooleanField(default=False),
        ),
    ]