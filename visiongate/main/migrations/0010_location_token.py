# Generated by Django 5.1.3 on 2024-11-23 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_location_device_location_status_alter_event_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='token',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Токен сессии устройства'),
        ),
    ]
