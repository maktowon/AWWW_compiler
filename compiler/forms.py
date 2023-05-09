from django.forms import ModelForm
from .models import Directory, File


class DirectoryForm(ModelForm):
    class Meta:
        model = Directory
        fields = ('name', 'description')


class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ('name', 'description')
