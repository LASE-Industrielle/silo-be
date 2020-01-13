# Generated by Django 2.2.1 on 2020-01-13 12:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20200112_1257'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='measurement',
            name='percentage',
        ),
        migrations.AddField(
            model_name='measurement',
            name='charge',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='measurement',
            name='distance',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='silo',
            name='gap_bottom',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='silo',
            name='gap_top',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='measurement',
            name='value',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)]),
        ),
    ]
