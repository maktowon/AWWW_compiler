from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import File, Directory
from django.contrib.auth.forms import UserCreationForm


@login_required(login_url='login')
def home(request):
    root_folders = Directory.objects.filter(parent=None).filter(owner=request.user)
    root_files = File.objects.filter(parent=None).filter(owner=request.user)

    return render(request, 'compiler/main.html', {'root_folders': root_folders, 'root_files': root_files})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'compiler/register.html', {'form_register': form})


def login_to(request):
    message = ''
    if request.method == 'POST':
        user_name = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user_name = User.objects.get(username=user_name)
        except ObjectDoesNotExist:
            message = 'not a valid username'
            return render(request, 'compiler/login.html', {'message': message})
        user_authenticate = authenticate(request, username=user_name, password=password)
        if user_authenticate is not None:
            login(request, user_authenticate)
            return redirect('home')
        else:
            message = 'wrong pasword'
    return render(request, 'compiler/login.html', {'message': message})


@login_required(login_url='login')
def logout_my(request):
    logout(request)
    return redirect('home')


@login_required(login_url='login')
def show_code(request, pk):
    file = File.objects.get(id=pk)
    data = file.name
    root_folders = Directory.objects.filter(parent=None)
    root_files = File.objects.filter(parent=None)
    return render(request, 'compiler/show_code.html', {'root_folders': root_folders, 'root_files': root_files, 'data': data})

