from django.shortcuts import render
from django.http import JsonResponse
from .models import File, Directory


def home(request):
    root_folders = Directory.objects.filter(parent=None)
    root_files = File.objects.filter(parent=None)

    return render(request, 'compiler/main.html', {'root_folders': root_folders, 'root_files': root_files})


def show_code(request, pk):
    file = File.objects.get(id=pk)
    data = file.name
    root_folders = Directory.objects.filter(parent=None)
    root_files = File.objects.filter(parent=None)
    return render(request, 'compiler/show_code.html', {'root_folders': root_folders, 'root_files': root_files, 'data': data})

