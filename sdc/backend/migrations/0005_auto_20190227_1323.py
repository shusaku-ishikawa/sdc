# Generated by Django 2.1.5 on 2019-02-27 04:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_picture'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Picture',
            new_name='RecipeQuery',
        ),
    ]