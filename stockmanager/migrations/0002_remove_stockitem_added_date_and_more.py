# Generated by Django 5.2.3 on 2025-06-25 08:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmanager', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockitem',
            name='added_date',
        ),
        migrations.RemoveField(
            model_name='stockitem',
            name='price_per_unit',
        ),
        migrations.RemoveField(
            model_name='stockitem',
            name='quantity',
        ),
        migrations.AddField(
            model_name='stockitem',
            name='price_usd',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='stockitem',
            name='symbol',
            field=models.CharField(default='BTC', max_length=10),
        ),
        migrations.AlterField(
            model_name='stockitem',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.CreateModel(
            name='UserHolding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField(default=0.0)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stockmanager.stockitem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
