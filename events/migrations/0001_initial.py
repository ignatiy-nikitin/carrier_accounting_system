# Generated by Django 3.1.6 on 2021-03-03 14:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('NEW', 'Новый заказ'), ('READY_FOR_SHIPPING', 'Собран на складе отправителя'), ('SORTING', 'На складе транспортной компании'), ('DELIVERING', 'Доставляется (передан курьеру для доставки покупателю)'), ('DELAYED', 'Доставка не была выполнена в срок'), ('DONE', 'Доставлен'), ('CANCELED', 'Отменен')], max_length=64)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('comments', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('path', models.CharField(max_length=256)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='events.event')),
            ],
        ),
    ]