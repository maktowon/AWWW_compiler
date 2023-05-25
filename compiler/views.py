from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from .models import File, Directory, Section
from . import helpers
from django.contrib.auth.forms import UserCreationForm
from .forms import DirectoryForm, FileForm
import subprocess
import os



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
            message = 'wrong password'
    return render(request, 'compiler/login.html', {'message': message})


@login_required(login_url='login')
def logout_my(request):
    logout(request)
    return redirect('home')


@login_required(login_url='login')
def folder_details(request, pk):
    directory_form = {}
    file_form = {}
    submitted = False
    contains = False
    try:
        folder = Directory.objects.get(id=pk, active=True)
    except ObjectDoesNotExist:
        return render(request, 'compiler/not_valid.html')
    if folder.owner != request.user:
        return render(request, 'compiler/not_your.html')
    path = str(pk)
    if request.method == 'POST':
        if 'add_dir' in request.POST:
            directory_form = DirectoryForm(request.POST)
            if directory_form.is_valid():
                if folder.directory_set.all().filter(name=directory_form['name'].value()).filter(
                        active=True).count() > 0:
                    return HttpResponseRedirect(path + '?contains=True')
                new_directory = directory_form.save(commit=False)
                new_directory.owner = request.user
                new_directory.parent = folder
                new_directory.save()
                folder.change_mod_date_upstream()
                return HttpResponseRedirect(path + '?submitted=True')

        if 'add_file' in request.POST:
            file_form = FileForm(request.POST)
            if file_form.is_valid():
                if folder.file_set.all().filter(name=file_form['name'].value()).filter(active=True).count() > 0:
                    return HttpResponseRedirect(path + '?contains=True')
                new_file = file_form.save(commit=False)
                new_file.owner = request.user
                new_file.parent = folder
                new_file.save()
                folder.change_mod_date_upstream()
                return HttpResponseRedirect(path + '?submitted=True')
    else:
        directory_form = DirectoryForm
        file_form = FileForm
        if 'contains' in request.GET:
            contains = True
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'compiler/folder_details.html', {'folder': folder, 'directory_form': directory_form,
                                                            'file_form': file_form, 'submitted': submitted,
                                                            'contains': contains})


@login_required(login_url='login')
def root_folder(request):
    directory_form = {}
    file_form = {}
    submitted = False
    contains = False
    folder = None
    if request.method == 'POST':
        if 'add_dir' in request.POST:
            directory_form = DirectoryForm(request.POST)
            if directory_form.is_valid():
                if Directory.objects.filter(name=directory_form['name'].value()).filter(parent=None).filter(
                        active=True).filter(owner=request.user).count() > 0:
                    return HttpResponseRedirect('?contains=True')
                new_directory = directory_form.save(commit=False)
                new_directory.owner = request.user
                new_directory.save()
                return HttpResponseRedirect('?submitted=True')

        if 'add_file' in request.POST:
            file_form = FileForm(request.POST)
            if file_form.is_valid():
                if File.objects.filter(name=file_form['name'].value()).filter(parent=None).filter(
                        active=True).filter(owner=request.user).count() > 0:
                    return HttpResponseRedirect('?contains=True')
                new_file = file_form.save(commit=False)
                new_file.owner = request.user
                new_file.save()
                return HttpResponseRedirect('?submitted=True')
    else:
        directory_form = DirectoryForm
        file_form = FileForm
        if 'contains' in request.GET:
            contains = True
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'compiler/root_folder.html', {'folder': folder, 'directory_form': directory_form,
                                                         'file_form': file_form, 'submitted': submitted,
                                                         'contains': contains})


@login_required(login_url='login')
def folder_delete(request, pk):
    try:
        folder = Directory.objects.get(id=pk, active=True)
    except ObjectDoesNotExist:
        return render(request, 'compiler/not_valid.html')
    if folder.owner != request.user:
        return render(request, 'compiler/not_your.html')

    folder.set_folder_inactive()
    folder.change_mod_date_upstream()
    return redirect('home')


@login_required(login_url='login')
def file_delete(request, pk):
    try:
        file = File.objects.get(id=pk, active=True)
    except ObjectDoesNotExist:
        return render(request, 'compiler/not_valid.html')
    if file.owner != request.user:
        return render(request, 'compiler/not_your.html')

    file.active = False
    file.save()
    if file.parent is not None:
        file.parent.change_mod_date_upstream()
    return redirect('home')


@login_required(login_url='login')
def run(request):
    code = ""
    error = ""
    asm = ""
    root_folders = Directory.objects.filter(parent=None).filter(owner=request.user).filter(active=True)
    root_files = File.objects.filter(parent=None).filter(owner=request.user).filter(active=True)
    if request.method == "POST":
        code = request.POST['codearea']
        standard = request.POST['standard']
        optimizations = request.POST['optimizations']
        processor = request.POST['processor']
        MCSoption = request.POST['MCSoption']
        STM8option = request.POST['STM8option']
        Z80option = request.POST['Z80option']
        if processor == "":
            error = "PLEASE SELECT PROCESSOR"
            return render(request, 'compiler/main.html',
                          {'root_folders': root_folders, 'root_files': root_files, 'code': code,
                           'output': asm, 'error': error})
        if optimizations == "":
            error = "PLEASE SELECT OPTIMIZATION"
            return render(request, 'compiler/main.html',
                          {'root_folders': root_folders, 'root_files': root_files, 'code': code,
                           'output': asm, 'error': error})

        id = request.POST['file_id']
        try:
            name = File.objects.get(id=id).name
        except Exception:
            name = 'file'
        name += '.c'
        cpuoption = ""
        if processor == "mcs51":
            cpuoption = "--" + MCSoption
        elif processor == "stm8":
            cpuoption = "--" + STM8option
        elif processor == "z80":
            cpuoption = "--asm=" + Z80option

        optimizations = optimizations[:-1]
        processor = "-m" + processor
        try:
            with open(name, 'w') as f:
                f.write(code)
            result = subprocess.run(['sdcc', optimizations, '-S', '-std=' + standard, processor, cpuoption, name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                output = open(name[:-2] + '.asm', 'r').readlines()
                asm = helpers.asm_to_sections(output)
                if id != '':
                    file = File.objects.get(id=id)
                    file.code = code
                    file.save()
                    helpers.code_to_sections(file)
            else:
                error = result.stderr.decode('utf-8')
        except Exception as e:
            error = str(e)

        os.remove(str(name))
        os.remove(str(name[:-2] + '.asm'))
        return JsonResponse({'asm': asm, 'error': error})

    return render(request, 'compiler/main.html', {'root_folders': root_folders, 'root_files': root_files, 'code': code,
                                                  'output': asm, 'error': error})


def edit_sections(request):
    return render(request, 'compiler/edit_sections.html')
