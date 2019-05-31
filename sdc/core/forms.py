from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import *
from .models import *


class LoginForm(AuthenticationForm):
    """ログインフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control input-sm'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる

class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ('file',)

