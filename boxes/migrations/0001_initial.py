# Generated by Django 3.1.6 on 2021-03-03 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Box',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_code', models.CharField(max_length=64, unique=True, verbose_name='Код коробки в системе заказчика')),
                ('code', models.CharField(max_length=256, verbose_name='Маркировка')),
                ('width', models.FloatField(blank=True, help_text='Метры', null=True, verbose_name='Ширина')),
                ('height', models.FloatField(blank=True, help_text='Метры', null=True, verbose_name='Высота')),
                ('length', models.FloatField(blank=True, help_text='Метры', null=True, verbose_name='Длина')),
                ('weight', models.FloatField(blank=True, help_text='Общий вес в кг', null=True, verbose_name='Вес')),
                ('content_description', models.TextField(blank=True, null=True, verbose_name='Описание содержимого')),
                ('status', models.CharField(choices=[('NEW', 'Новый заказ'), ('READY_FOR_SHIPPING', 'Собран на складе отправителя'), ('SORTING', 'На складе транспортной компании'), ('DELIVERING', 'Доставляется (передан курьеру для доставки покупателю)'), ('DELAYED', 'Доставка не была выполнена в срок'), ('DONE', 'Доставлен'), ('CANCELED', 'Отменен')], default='NEW', help_text='По умолчанию: NEW', max_length=32, verbose_name='Состояние коробки')),
            ],
            options={
                'verbose_name': 'box',
                'verbose_name_plural': 'boxes',
            },
        ),
    ]