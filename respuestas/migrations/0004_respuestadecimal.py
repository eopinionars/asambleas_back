# Generated by Django 3.0 on 2020-05-21 14:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0009_auto_20200521_0915'),
        ('respuestas', '0003_auto_20200521_1341'),
    ]

    operations = [
        migrations.CreateModel(
            name='RespuestaDecimal',
            fields=[
                ('respuesta_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='respuestas.Respuesta')),
                ('respuesta_decimal', models.DecimalField(decimal_places=3, max_digits=4)),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pregunta_decimal', to='eventos.PreguntaDecimal')),
            ],
            bases=('respuestas.respuesta',),
        ),
    ]