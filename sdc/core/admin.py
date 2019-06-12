from django.contrib import admin
from .models import *
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .forms import *
from django.urls import path
from django.shortcuts import render
import xlrd
import pandas as pd
from django.http import *
import xlsxwriter
from io import BytesIO as IO
import math
import re

class MyUploadedErrorRecordAdmin(admin.ModelAdmin):
    list_display = ('file', 'reason')

class MyUploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')
    product_columns = [
        'qr',
        'name',
        'manufacturer',
        'seller',
        'ingredients',
        'allergens',
        'calory',
        'height_in_mm',
        'width_in_mm',
        'qr_x_offset_in_mm',
        'qr_y_offset_in_mm',
        'otherInfo'
    ]
    recipe_columns = [
        'product',
        'name', 
        'recipe'
    ]
    change_list_template = "my_upload_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-excel/', self.import_excel),
            path('export-excel/', self.export_excel),
        ]
        return my_urls + urls

    def export_excel(self, request):
        
        io = IO()
        product_headers = [
            "ID(整数値)",
            "QR_ID(文字列(255))",
            "食品名(文字列(２０文字まで))",
            "製造元(文字列(２０文字まで))",
            "販売元(文字列(２０文字まで))",
            "原材料(文字列(５０文字まで))",
            "アレルゲン(文字列(全角５０文字まで))",
            "カロリー(kal）(整数4桁)",
            "高さ(mm)(整数4桁)",
            "幅(mm)(整数4桁)",
            "QR位置-x(mm)(整数4桁)",
            "QR位置-y(mm)(整数4桁)",
            "付加情報(文字列(255))",
        ]
        recipe_headers = [
            'レシピID',
            '食品ID',
            'QR_ID',
            '食品名',
            'レシピ名(文字列(２０文字まで))',
            'ステージ1 温度',
            'ステージ1 出力W',
            'ステージ2 温度',
            'ステージ2 出力W',
            'ステージ3 温度',
            'ステージ3 出力W',
            'ステージ4 温度',
            'ステージ4 出力W',
            'ステージ5 温度',
            'ステージ5 出力W',
            'ステージ6 温度',
            'ステージ6 出力W',
            'ステージ7 温度',
            'ステージ7 出力W',
            'ステージ8 温度',
            'ステージ8 出力W',
        ]
        df_product = pd.DataFrame(list(Product.objects.all().values_list('id', 'qr', 'name', 'manufacturer', 'seller', 'ingredients', 'allergens', 'calory', 'height_in_mm', 'width_in_mm', 'qr_x_offset_in_mm', 'qr_y_offset_in_mm', 'otherInfo' )))
        df_recipe = pd.DataFrame(index = [], columns = recipe_headers)
        df_recipe['レシピID'] = list(Recipe.objects.all().values_list('id', flat=True))
        df_recipe['食品ID'] = list(Recipe.objects.all().values_list('product__id', flat = True))
        df_recipe['QR_ID'] = list(Recipe.objects.all().values_list('product__qr', flat = True))
        df_recipe['食品名'] = list(Recipe.objects.all().values_list('product__name', flat = True))
        df_recipe['レシピ名(文字列(２０文字まで))'] = list(Recipe.objects.all().values_list('name', flat = True))
        
        for i in range(16):
            li = []
            for recipe in Recipe.objects.all():
                recipe_list = recipe.recipe.split(',')

                if i < len(recipe_list):
                    li.append(recipe_list[i])
                else:
                    li.append('')
            if i % 2 == 0:
                df_recipe['ステージ' + str(math.floor(i/2) + 1) + ' 温度'] = li
            else:
                df_recipe['ステージ' + str(math.floor(i/2) + 1) + ' 出力W'] = li
            li = []

        writer = pd.ExcelWriter(io, engine='xlsxwriter')

        # Write each dataframe to a different worksheet.
        df_product.to_excel(writer, sheet_name='食品',index = False, header = product_headers)
        df_recipe.to_excel(writer, sheet_name='レシピ', index = False, header = recipe_headers)
        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

        io.seek(0)
        workbook = io.getvalue()

        response = HttpResponse(workbook, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s' % 'product_and_recipe.xlsx'

        return response

    def import_excel(self, request):
        if request.method == "POST":
            
            err_count = 0

            form = UploadedFileForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                obj = form.save()
                df = pd.read_excel(obj.file.path,  dtype=str, header=[0], sheet_name = 0)
                df = df.fillna('')
                for index, row in df.iterrows():
                    params = {}
                    for i in range(len(self.product_columns)): 
                        params[self.product_columns[i]] = row[i + 1]

                    id = row[0]
                    if id != '':
                        
                        try:  
                            p = Product.objects.get(id = id)
                            print('id :' + str(id) + ' の食品を修正します')
                        except:
                            print('id :' + str(id) + ' の食品を追加します')
                            p = Product(id = id)
                        
                        f = ProductForm(params, instance = p)
                    else:
                        print('自動採番で食品を追加します')
                        f = ProductForm(params)
                    
                    if f.is_valid():
                        f.save()
                    else:
                        error_count += 1
                        for key in f.errors.as_data():
                            for error in f.errors[key].as_data():
                                print(str(error))
                                err = UploadedErrorRecord()
                                err.file = obj
                                err.reason = key + ': ' + str(error)
                                err.save()
               
                df = pd.read_excel(obj.file.path,  dtype=str, header=[0], sheet_name = 1)
                df = df.fillna('')
                for index, row in df.iterrows():
                    params = {}

                    # product
                    params[self.recipe_columns[0]] = row[1]
                    # name 
                    params[self.recipe_columns[1]] = row[4]
                    

                    recipe_str = ""
                    for s in range(1, 9):
                        # target temp
                        
                        temp = row[5 + (s-1) * 2]
                        power = row[6 + (s-1) * 2]
                        if temp != '' and power != '':
                            recipe_str += str(temp) + ',' + str(power)    
                            recipe_str += ','
                        else:
                            break
                    
                    params['recipe'] = re.sub(',$', '', recipe_str)
                
                    id = row[0]
                    if id != '':
                        try:
                            r = Recipe,objects.get(id = id)
                            print('id :' + str(id) + ' のレシピを修正します')
                        except:
                            print('id :' + str(id) + ' でレシピを追加します')
                            r = Recipe(id = id)
                        f = RecipeForm(params, instance = r)    
                    else:
                        print('自動採番でレシピを追加します')
                        f = RecipeForm(params)

                    if f.is_valid():
                        f.save()
                    else:
                        error_count += 1
                        for key in f.errors.as_data():
                            for error in f.errors[key].as_data():
                                print(str(error))
                                err = UploadedErrorRecord()
                                err.file = obj
                                err.reason = key + ': ' + str(error)
                                err.save()

            else:
                print(form.errors)

            
            if err_count == 0:
                self.message_user(request, "取り込みました")
                return HttpResponseRedirect('/admin/core/uploadedfile')
            else:
                self.message_user(request, "{err}件エラーがありました".format(err_count))
                return HttpResponseRedirect('/admin/core/uploadederrorrecord')
        form = UploadedFileForm()
        payload = {"form": form}
        return render(
            request, "my_import_form.html", payload
        )


class MyProductAdmin(admin.ModelAdmin):
    list_display = ('id' ,'qr', 'name', 'height_in_mm', 'width_in_mm', 'qr_y_offset_in_mm', 'qr_x_offset_in_mm', 'otherInfo')
    
class MyRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'name', 'recipe')
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
admin.site.register(UploadedFile, MyUploadedFileAdmin)
admin.site.register(UploadedErrorRecord, MyUploadedErrorRecordAdmin)


