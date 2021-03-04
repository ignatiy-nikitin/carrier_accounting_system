# Generated by Django 3.1.6 on 2021-03-03 14:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shipments', '0001_initial'),
        ('boxes', '0002_box_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='box',
            name='shipment',
            field=models.ForeignKey(blank=True, help_text='Указывается при создании отправления', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='boxes', to='shipments.shipment', verbose_name='Отправление'),
        ),
    ]
