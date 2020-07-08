# Generated by Django 3.0 on 2020-07-06 00:16

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0029_quorum_imuebles_registrados'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quorum',
            name='imuebles_registrados',
        ),
        migrations.CreateModel(
            name='InmueblesQuorum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inmuebles_registrados', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(default='', max_length=4, null=True), blank=True, null=True, size=None)),
                ('registrado', models.BooleanField(default=False)),
                ('evento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evento_inmuebles_quorum', to='eventos.Evento')),
            ],
        ),
        migrations.AddField(
            model_name='quorum',
            name='inmuebles_registrados',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='quorum_inmuebles_registrados', to='eventos.InmueblesQuorum'),
        ),
    ]
