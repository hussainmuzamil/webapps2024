# Generated by Django 5.0.4 on 2024-04-19 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='principal',
            name='last_name',
            field=models.CharField(default='', max_length=200),
        ),
    ]