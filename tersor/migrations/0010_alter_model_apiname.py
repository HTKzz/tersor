# Generated by Django 3.2.20 on 2023-08-21 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tersor', '0009_alter_model_apiname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='model',
            name='apiName',
            field=models.SlugField(null=True, unique=True),
        ),
    ]
