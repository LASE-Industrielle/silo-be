# Generated by Django 2.2.1 on 2020-01-12 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20191223_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='measurement',
            name='percentage',
            field=models.FloatField(default=-1),
        ),
        migrations.AlterField(
            model_name='measurement',
            name='value',
            field=models.FloatField(default=-1),
        ),
    ]
