# Generated by Django 3.2.20 on 2023-08-21 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tersor', '0008_input_api_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='model',
            name='apiName',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
    ]
