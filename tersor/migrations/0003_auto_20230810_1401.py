# Generated by Django 3.2.20 on 2023-08-10 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tersor', '0002_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='model',
            name='imagebox',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='model',
            name='inputbox',
            field=models.IntegerField(null=True),
        ),
    ]
