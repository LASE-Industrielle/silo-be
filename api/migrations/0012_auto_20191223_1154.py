# Generated by Django 2.2.1 on 2019-12-23 10:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0011_auto_20191223_1144'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sensor',
            name='silo',
        ),
        migrations.RemoveField(
            model_name='silo',
            name='user',
        ),
        migrations.AddField(
            model_name='sensor',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='silo',
            name='sensor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Sensor'),
        ),
    ]
