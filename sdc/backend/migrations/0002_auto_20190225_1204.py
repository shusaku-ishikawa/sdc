# Generated by Django 2.1.5 on 2019-02-25 03:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField(default=1, verbose_name='バージョン')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='qr_at_width',
            field=models.FloatField(default=1, verbose_name='QR位置(横)'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='qr_at_height',
            field=models.FloatField(verbose_name='QR位置(縦)'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Product', verbose_name='商品'),
        ),
    ]