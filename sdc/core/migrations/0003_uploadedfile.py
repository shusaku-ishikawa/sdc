# Generated by Django 2.1.5 on 2019-05-31 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20190531_1508'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(choices=[('1', '食品'), ('2', 'レシピ')], max_length=255, verbose_name='内容')),
                ('file', models.FileField(upload_to='from_admin', verbose_name='ファイル')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='処理日')),
                ('rec_count', models.IntegerField(default=0, verbose_name='件数')),
            ],
            options={
                'verbose_name': 'アップロードファイル',
                'verbose_name_plural': 'アップロードファイル',
            },
        ),
    ]
