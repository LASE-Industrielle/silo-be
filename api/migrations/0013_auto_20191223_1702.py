# Generated by Django 2.2.1 on 2019-12-23 16:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20191223_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measurement',
            name='value',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)]),
        ),
    ]
