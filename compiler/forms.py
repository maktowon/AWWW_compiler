from django.forms import ModelForm
from .models import Directory, File, Section
from django import forms


class DirectoryForm(ModelForm):
    class Meta:
        model = Directory
        fields = ('name', 'description')


class NewDirectoryForm(ModelForm):
    class Meta:
        model = Directory
        fields = ('parent', 'name', 'description')


class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ('name', 'description')


class NewFileForm(ModelForm):
    class Meta:
        model = File
        fields = ('parent', 'name', 'description')


class SectionForm(ModelForm):
    class Meta:
        model = Section
        fields = ('file', 'name', 'description', 'begin', 'end', 'type', 'parent')


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
