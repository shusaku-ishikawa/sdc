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

class MyUploadedErrorRecordAdmin(admin.ModelAdmin):
    list_display = ('file', 'reason')

class MyUploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')

    change_list_template = "my_upload_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-excel/', self.import_excel),
        ]
        return my_urls + urls

    def import_excel(self, request):
        if request.method == "POST":
            err_count = 0

            form = UploadedFileForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                obj = form.save()
                df = pd.read_excel(obj.file.path,  dtype=str, header=[0, 1], sheet_name = 0)
                df = df.fillna('')
                for index, row in df.iterrows():
                    try:
                        id = row[0]
                        if id != '':
                            try:
                                p = Product,objects.get(id = id)
                            except:
                                p = Product(id = id)
                        else:
                            p = Product()
                        
                        p.qr = row[1]
                        p.name = row[2]
                        p.manufacturer = row[3]
                        p.seller = row[4]
                        p.ingredients = row[5]
                        p.allergens = row[6]
                        p.calory = row[7]
                        p.height_in_mm = row[8]
                        p.width_in_mm = row[9]
                        p.qr_x_offset_in_mm = row[10]
                        p.qr_y_offset_in_mm = row[11]
                        p.other_info = row[12]      
                        p.save()
                    except Exception as e:
                        err_count += 1
                        err = UploadedErrorRecord(file = obj)
                        err.reason = str(e.args)
                        err.save()

                df = pd.read_excel(obj.file.path,  dtype=str, header=[0, 1], sheet_name = 1)
                df = df.fillna('')
                for index, row in df.iterrows():
                    try:
                        id = row[0]
                        if id != '':
                            try:
                                r = Recipe,objects.get(id = id)
                            except:
                                r = Recipe(id = id)
                        else:
                            r = Recipe()
                        
                        r.product = Product.objects.get(id = row[1])
                        r.name = row[4]

                        recipe_str = ""
                        for s in range(1, 9):
                            # target temp
                            
                            temp = row[5 + (s-1) * 2]
                            power = row[6 + (s-1) * 2]
                            if temp != '' and power != '':
                                recipe_str += str(temp) + ',' + str(power)
                                if s != 8:
                                    recipe_str += ','
                            else:
                                break

                        r.recipe = recipe_str
                        r.save()    
                            
                    except Exception as e:
                        err_count += 1
                        err = UploadedErrorRecord(file = obj)
                        err.reason = str(e.args)
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
admin.site.register(UploadedErrorRecord, MyUploadedErrorRecordAdmin)
admin.site.register(UploadedFile, MyUploadedFileAdmin)


