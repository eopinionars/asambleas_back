# Generated by Django 3.0 on 2020-05-16 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0006_auto_20200516_1842'),
    ]

    operations = [
        migrations.AddField(
            model_name='preguntamultiple',
            name='puntajeCoeficiente',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='preguntamultiple',
            name='esMultipleResp',
            field=models.BooleanField(default=False),
        ),
    ]