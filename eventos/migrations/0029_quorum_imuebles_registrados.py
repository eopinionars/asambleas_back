# Generated by Django 3.0 on 2020-07-03 02:02

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0028_evento_codconferencia'),
    ]

    operations = [
        migrations.AddField(
            model_name='quorum',
            name='imuebles_registrados',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(default='', max_length=4, null=True), blank=True, default=[], null=True, size=None),
        ),
    ]
