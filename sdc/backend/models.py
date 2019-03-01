from django.db import models

# Create your models here.
class Maker(models.Model):
    
    name = models.CharField(
        verbose_name = '名称',
        max_length = 100
    )

class Product(models.Model):
    qr = models.CharField(
        verbose_name = 'QRコード',
        max_length = 100,
        unique = True
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

class Recipe(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name = '商品',
        on_delete = models.CASCADE
    )
    version = models.IntegerField(
        verbose_name = 'バージョン',
        default = 1
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



