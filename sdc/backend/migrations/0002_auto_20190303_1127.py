# Generated by Django 2.1.5 on 2019-03-03 11:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='oven',
            old_name='oven_code',
            new_name='code',
        ),
    ]
