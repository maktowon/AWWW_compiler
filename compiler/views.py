from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from . import helpers
from .forms import *
import subprocess
import os


def register(request):
    message = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            message = 'Passwords do not match.'
        elif User.objects.filter(username=username).exists():
            message = 'Username already taken.'
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('home')

    return render(request, 'compiler/register.html', {'message': message})


@login_required(login_url='login')
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
        directory_form = DirectoryForm()
        file_form = FileForm()
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
        directory_form = DirectoryForm()
        file_form = FileForm()
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
        return JsonResponse({'success': False, 'message': 'Folder does not exist.'})

    if folder.owner != request.user:
        return JsonResponse({'success': False, 'message': 'You are not the owner of this folder.'})

    folder.set_folder_inactive()
    folder.change_mod_date_upstream()
    return JsonResponse({'success': True, 'message': 'Folder deleted successfully.'})


@login_required(login_url='login')
def file_delete(request, pk):
    try:
        file = File.objects.get(id=pk, active=True)
    except ObjectDoesNotExist:
        return JsonResponse({'success': False, 'message': 'File does not exist.'})

    if file.owner != request.user:
        return JsonResponse({'success': False, 'message': 'You are not the owner of this file.'})

    file.active = False
    file.save()
    if file.parent is not None:
        file.parent.change_mod_date_upstream()
    return JsonResponse({'success': True, 'message': 'File deleted successfully.'})


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
            return JsonResponse({'asm': asm, 'error': error})
        if optimizations == "":
            error = "PLEASE SELECT OPTIMIZATION"
            return JsonResponse({'asm': asm, 'error': error})

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

        if os.path.exists(str(name)):
            os.remove(str(name))
        if os.path.exists(str(name[:-2] + '.asm')):
            os.remove(str(name[:-2] + '.asm'))
        return JsonResponse({'asm': asm, 'error': error})

    directory_form = NewDirectoryForm()
    directory_form.fields['parent'].queryset = Directory.objects.filter(owner=request.user, active=True)
    file_form = NewFileForm()
    file_form.fields['parent'].queryset = Directory.objects.filter(owner=request.user, active=True)
    section_form = SectionForm()
    section_form.fields['file'].queryset = File.objects.filter(owner=request.user, active=True)
    section_form.fields['parent'].queryset = Section.objects.filter(owner=request.user)
    return render(request, 'compiler/main.html', {'root_folders': root_folders, 'root_files': root_files, 'code': code,
                                                  'asm': asm, 'error': error, 'directory_form': directory_form,
                                                  'file_form': file_form, 'section_form': section_form})


def create_section(request):
    if request.method == 'POST':
        section_form = SectionForm(request.POST)

        if section_form.is_valid():
            new_section = section_form.save(commit=False)
            new_section.owner = request.user
            new_section.save()


def edit_sections(request):
    section_form = SectionForm()
    section_form.fields['file'].queryset = File.objects.filter(owner=request.user, active=True)
    section_form.fields['parent'].queryset = Section.objects.filter(owner=request.user)
    if request.method == 'POST':
        section_form = SectionForm(request.POST)

        if section_form.is_valid():
            new_section = section_form.save(commit=False)
            new_section.owner = request.user
            new_section.save()
    return render(request, 'compiler/create_section.html', {'section_form': section_form})
