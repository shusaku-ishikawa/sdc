from django.db import models
from unixtimestampfield.fields import UnixTimeStampField
from django.utils.translation import ugettext_lazy as _

# Create your models here.
class Maker(models.Model):
    class Meta:
        verbose_name = '電子レンジメーカ'
        verbose_name_plural = '電子レンジメーカ'

    def __str__(self):
        return str(self.name)

    name = models.CharField(
        verbose_name = '名称',
        max_length = 100
    )

class Product(models.Model):
    class Meta:
        verbose_name = '食品'
        verbose_name_plural = '食品'

    def __str__(self):
        return str(self.name)

    qr = models.CharField(
        verbose_name = 'qr',
        max_length = 255,
        unique = True
    )

    name = models.CharField(
        verbose_name = '食品名',
        max_length = 100,
        null = False,
        blank = False
    )
    
    manufacturer = models.CharField(
        verbose_name = '製造元',
        max_length = 255,
        null = True,
        blank = True,
    )

    seller = models.CharField(
        verbose_name = '販売元',
        max_length = 255,
        null = True,
        blank = True,
    )
    ingredients = models.CharField(
        verbose_name = '原材料',
        max_length = 255,
        null = True,
        blank = True,
    )
    allergens = models.CharField(
        verbose_name = 'アレルゲン',
        max_length = 255,
        null = True,
        blank = True,
    )
    calory = models.FloatField(
        verbose_name = 'カロリー',
        null = True,
        blank = True,
    )
    other_info = models.CharField(
        verbose_name = "付加情報",
        max_length = 255
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
    class Meta:
        verbose_name = 'レシピ'
        verbose_name_plural = 'レシピ'

    def __str__(self):
        return str(self.name)

    product = models.ForeignKey(
        Product,
        verbose_name = '商品',
        on_delete = models.CASCADE
    )
    
    name = models.CharField(
        verbose_name = 'レシピ名',
        max_length = 255
    )
    recipe = models.CharField(
        verbose_name = 'レシピ',
        max_length = 255
    )


class Oven(models.Model):
    class Meta:
        verbose_name = '電子レンジ機種'
        verbose_name_plural = '電子レンジ機種'

    def __str__(self):
        return str(self.model_name)

    code = models.CharField(
        verbose_name = '機種コード',
        max_length = 255,
        unique = True,
        null = False,
        blank = False
    )

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

    channel_info = models.CharField(
        verbose_name = "チャネル情報",
        max_length = 255,
    )

class RecipeQuery(models.Model):
    class Meta:
        verbose_name = 'レシピ検索履歴'
        verbose_name_plural = 'レシピ検索履歴'

    def __str__(self):
        return str(self.model_name)

    image = models.ImageField(
        verbose_name = '画像',
        upload_to = 'from_microwaves/'
    )
    oven = models.ForeignKey(
        Oven,
        verbose_name = "機種",
        on_delete = models.CASCADE
    )
    received_at = UnixTimeStampField(
        verbose_name = _('問い合わせ日時'), 
        use_numeric = True,  
        auto_now_add = True,
    )


