# Generated by Django 2.2.1 on 2019-05-09 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20190509_0928'),
    ]

    operations = [
        migrations.AddField(
            model_name='silo',
            name='percentage',
            field=models.FloatField(default=0),
        ),
    ]
