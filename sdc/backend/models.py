from django.db import models

# Create your models here.
class Maker(models.Model):
    
    name = models.CharField(
        verbose_name = '名称',
        max_length = 100
    )

class Product(models.Model):
    jan = models.CharField(
        verbose_name = 'jan',
        max_length = 13,
    )

    version = models.CharField(
        verbose_name = "バージョン",
        max_length = 10,
    )

    name = models.CharField(
        verbose_name = '食品名',
        max_length = 100,
        null = False,
        blank = False
    )
    
    height = models.FloatField(
        verbose_name = 'サイズ(高さ)'
    )

    width = models.FloatField(
        verbose_name = 'サイズ(幅)'
    )

    qr_at_height = models.FloatField(
        verbose_name = 'QR位置(縦)'
    )
    qr_at_width = models.FloatField(
        verbose_name = 'QR位置(横)'
    )
    
    info = models.CharField(
        verbose_name = "付加情報",
        max_length = 255
    )

class Recipe(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name = '商品',
        on_delete = models.CASCADE
    )

class RecipeQuery(models.Model):

    image = models.ImageField(
        verbose_name = '画像',
        upload_to = 'from_microwaves/'
    )
    channels = models.CharField(
        verbose_name = "庫内情報",
        max_length = 255,
    )

class Oven(models.Model):
    maker_name = models.CharField(
        verbose_name = "メーカ",
        max_length = 100,
    )
    model_name = models.CharField(
        verbose_name = "機種名",
        max_length = 100,
    )
    floor_width_in_cm = models.IntegerField(
        verbose_name = "底面幅",
    )

    floor_height_in_cm = models.IntegerField(
        verbose_name = "底面高さ",
    )

    floor_height_in_cm = models.IntegerField(
        verbose_name = "底面高さ",
    )
    channel_info = models.CharField(
        verbose_name = "チャネル情報",
        max_length = 255,
    )


