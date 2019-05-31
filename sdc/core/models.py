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

class UploadedFile(models.Model):
    class Meta:
        verbose_name = 'アップロードファイル'
        verbose_name_plural = 'アップロードファイル'

    file = models.FileField(
        verbose_name = 'ファイル',
        upload_to = 'from_admin',
    )
    uploaded_at = models.DateTimeField(
        verbose_name = '処理日',
        auto_now_add = True
    )
    rec_count = models.IntegerField(
        verbose_name = '件数',
        default = 0
    )
class UploadedErrorRecord(models.Model):
    class Meta:
        verbose_name = 'アップロードエラー'
        verbose_name_plural = 'アップロードエラー'
    file = models.ForeignKey(
        verbose_name = 'ファイル',
        to = UploadedFile,
        on_delete = models.CASCADE,
    )
    reason = models.CharField(
        verbose_name = 'エラー事由',
        max_length = 255,
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
        max_length = 255,
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

    
    height_in_mm = models.FloatField(
        verbose_name = '高さ(mm)'
    )

    width_in_mm = models.FloatField(
        verbose_name = '幅(mm)'
    )

    qr_x_offset_in_mm = models.FloatField(
        verbose_name = 'QR位置-x(mm)'
    )
    qr_y_offset_in_mm = models.FloatField(
        verbose_name = 'QR位置-y(mm)'
    )
    
    other_info = models.CharField(
        verbose_name = "付加情報",
        max_length = 255,
        blank = True,
        null = True,
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
        max_length = 255,
    )
    model_name = models.CharField(
        verbose_name = "機種名",
        max_length = 100,
    )
    floor_width_in_mm = models.IntegerField(
        verbose_name = "底面幅",
    )

    floor_height_in_mm = models.IntegerField(
        verbose_name = "底面高さ",
    )


class OvenChannel(models.Model):
    class Meta:
        verbose_name = 'チャネル'
        verbose_name_plural = 'チャネル'
    def __str__(self):
        return ''
    
    oven = models.ForeignKey(
        to = Oven,
        verbose_name = 'レンジ',
        on_delete = models.CASCADE,
        related_name = 'channels'
    )
    seq = models.IntegerField(
        verbose_name = 'チャネル番号'
    )
    x_offset_in_mm = models.FloatField(
        verbose_name = '水平方向オフセット(mm)',
    )
    y_offset_in_mm = models.FloatField(
        verbose_name = '垂直方向オフセット(mm)',
    )
    width_in_mm = models.FloatField(
        verbose_name = '幅(mm)'
    )
    height_in_mm = models.FloatField(
        verbose_name = '高さ(mm)'
    )
    

class RecipeQuery(models.Model):
    class Meta:
        verbose_name = 'レシピ検索履歴'
        verbose_name_plural = 'レシピ検索履歴'

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

class History(models.Model):
    class Meta:
        verbose_name = '調理履歴'
        verbose_name_plural = '調理履歴'
    
    cooked_at =  UnixTimeStampField(
        verbose_name = _('調理完了日時'), 
        use_numeric = True,  
    )
    corresponding_query = models.ForeignKey(
        RecipeQuery,
        verbose_name = '問い合わせ',
        on_delete  = models.CASCADE
    )
    power_consumed = models.FloatField(
        verbose_name = '消費電力'
    )
    other_info = models.TextField(
        verbose_name = '付加情報',
        blank = True,
        null = True
    )   
class HistoryByChannel(models.Model):
    class Meta:
        verbose_name = 'チャネル毎調理履歴'
        verbose_name_plural = 'チャネル毎調理履歴'
    
    history = models.ForeignKey(
        History,
        verbose_name = '調理履歴',
        on_delete = models.CASCADE
    )
    channel = models.IntegerField(
        verbose_name= 'チャネル',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name = '利用レシピ',
        on_delete = models.CASCADE
    )
    surf_temp_before = models.FloatField(
        verbose_name = '開始表面温度'
    )
    
    surf_temp_after = models.FloatField(
        verbose_name = '終了表面温度'
    )
    seconds_taken = models.IntegerField(
        verbose_name = '調理時間'
    )