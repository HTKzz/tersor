# Generated by Django 3.2.20 on 2023-08-14 03:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tersor', '0006_delete_ten'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='input',
            name='api_id',
        ),
    ]
