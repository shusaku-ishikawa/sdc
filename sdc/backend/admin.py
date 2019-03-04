from django.contrib import admin
from .models import Product, Recipe, RecipeQuery, Oven
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _


class MyProductAdmin(admin.ModelAdmin):
    list_display = ('qr', 'name', 'height', 'width', 'qr_at_height', 'qr_at_width', 'info')

class MyRecipeAdmin(admin.ModelAdmin):
    list_display = ('product', 'recipe')
    
class MyOvenAdmin(admin.ModelAdmin):
    list_display = ('code', 'maker_name', 'model_name', 'floor_width_in_cm', 'floor_height_in_cm')

class MyRecipeQueryAdmin(admin.ModelAdmin):
    list_display = ('image', 'oven', 'received_at')

admin.site.register(Product, MyProductAdmin)
admin.site.register(Recipe, MyRecipeAdmin)
admin.site.register(Oven, MyOvenAdmin)
admin.site.register(RecipeQuery, MyRecipeQueryAdmin)
