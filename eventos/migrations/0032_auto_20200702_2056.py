# Generated by Django 3.0 on 2020-07-03 01:56

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0031_auto_20200702_1705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quorum',
            name='imuebles_registrados',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(default='', max_length=4, null=True), blank=True, null=True, size=None),
        ),
    ]
