# Generated by Django 3.0 on 2020-05-20 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0013_auto_20200519_2149'),
    ]

    operations = [
        migrations.AddField(
            model_name='apoderado',
            name='sumado',
            field=models.BooleanField(default=False),
        ),
    ]