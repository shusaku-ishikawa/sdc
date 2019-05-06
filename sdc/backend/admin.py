from django.contrib import admin
from .models import *
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _


class MyProductAdmin(admin.ModelAdmin):
    list_display = ('qr', 'name', 'height_in_mm', 'width_in_mm', 'qr_y_offset_in_mm', 'qr_x_offset_in_mm', 'other_info')

class MyRecipeAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'recipe')
    ordering = ('name',)
class MyOvenAdmin(admin.ModelAdmin):
    list_display = ('code', 'maker_name', 'model_name', 'floor_width_in_mm', 'floor_height_in_mm')
    
class MyChannelAdmin(admin.ModelAdmin):
    list_display = ('oven', 'seq', 'x_offset_in_mm', 'y_offset_in_mm', 'width_in_mm', 'height_in_mm')
class MyRecipeQueryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'image', 'oven', 'received_at')

class MyHisotryByChannelAdmin(admin.ModelAdmin):
    list_display = ('history', 'channel', 'recipe', 'surf_temp_before', 'surf_temp_after', 'seconds_taken')

admin.site.register(Product, MyProductAdmin)
admin.site.register(Recipe, MyRecipeAdmin)
admin.site.register(Oven, MyOvenAdmin)
admin.site.register(OvenChannel, MyChannelAdmin)
