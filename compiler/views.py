from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .models import File, Directory, Section
from django.contrib.auth.forms import UserCreationForm
from .forms import DirectoryForm, FileForm
import subprocess
import os
import re


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
    try:
        file = File.objects.get(id=pk, active=True)
    except ObjectDoesNotExist:
        return render(request, 'compiler/not_valid.html')
    if file.owner != request.user:
        return render(request, 'compiler/not_your.html')
    data = file.name
    root_folders = Directory.objects.filter(parent=None)
    root_files = File.objects.filter(parent=None)
    return render(request, 'compiler/show_code.html',
                  {'root_folders': root_folders, 'root_files': root_files, 'data': data})


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
                change_mod_date_upstream(folder)
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
                change_mod_date_upstream(folder)
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
                        active=True).count() > 0:
                    return HttpResponseRedirect('?contains=True')
                new_directory = directory_form.save(commit=False)
                new_directory.owner = request.user
                new_directory.save()
                return HttpResponseRedirect('?submitted=True')

        if 'add_file' in request.POST:
            file_form = FileForm(request.POST)
            if file_form.is_valid():
                if File.objects.filter(name=file_form['name'].value()).filter(parent=None).filter(
                        active=True).count() > 0:
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


def change_mod_date_upstream(folder):
    if folder is not None:
        folder.save()
        change_mod_date_upstream(folder.parent)


def set_folder_inactive(folder):
    folder.active = False
    folder.save()
    for file in folder.file_set.all():
        file.active = False
        file.save()
    for subfolder in folder.directory_set.all():
        set_folder_inactive(subfolder)


@login_required(login_url='login')
def folder_delete(request, pk):
    try:
        folder = Directory.objects.get(id=pk, active=True)
    except ObjectDoesNotExist:
        return render(request, 'compiler/not_valid.html')
    if folder.owner != request.user:
        return render(request, 'compiler/not_your.html')

    set_folder_inactive(folder)
    change_mod_date_upstream(folder.parent)
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
    change_mod_date_upstream(file.parent)
    return redirect('home')


def asm_to_sections(content):
    reg = r"^;[\t\w]*[-]+"
    header = ""
    section = ""
    ret = []
    now = []

    matches = 0
    for line in content:
        if re.match(reg, line) is not None:
            matches += 1
        if matches % 2 == 1:
            if header != "" and section != "":
                now.append(header)
                now.append(section)
                ret.append(now)
                header = ""
                section = ""
                now = []
            header += line
        else:
            section += line
    if header != ret[-1][0] or section != ret[-1][0]:
        now.append(header)
        now.append(section)
        ret.append(now)

    return ret


@login_required(login_url='login')
def run(request):
    code = ""
    error = ""
    asm = ""
    if request.method == "POST":
        code = request.POST['codearea']
        standard = request.POST['standard']
        optimizations = request.POST['optimizations']
        processor = request.POST['processor']
        dependent = request.POST['dependent']
        MCSoption = request.POST['MCSoption']
        STM8option = request.POST['STM8option']
        Z80option = request.POST['Z80option']
        id = request.POST['file_id']
        cpuoption = ""
        if processor == "MCS51":
            cpuoption = "--" + MCSoption
        elif processor == "STM8":
            cpuoption = "--asm=" + STM8option
        elif processor == "Z80":
            cpuoption = "--" + Z80option

        print(standard, optimizations, processor, dependent, cpuoption)
        try:
            with open('file.c', 'w') as f:
                f.write(code)

            result = subprocess.run(['sdcc', '-S', 'file.c'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                output = open('file.asm', 'r').readlines()
                asm = asm_to_sections(output)
                if id != '':
                    file = File.objects.get(id=id)
                    file.code = code
                    file.save()
            else:
                error = result.stderr.decode('utf-8')
        except Exception as e:
            error = str(e)

        os.remove('file.c')

    root_folders = Directory.objects.filter(parent=None).filter(owner=request.user)
    root_files = File.objects.filter(parent=None).filter(owner=request.user)

    return render(request, 'compiler/main.html', {'root_folders': root_folders, 'root_files': root_files, 'code': code,
                                                  'output': asm, 'error': error})


def code_to_sections(file):
    sections_to_delete = Section.objects.filter(file=file)
    sections_to_delete.delete()
    lines = file.code.splitlines()
    start_asm = r"^[\t\w]*__asm__"
    end_asm = r"^[\t\w]*);"
    directive = r"^[\t\w]*#"
    comment = r"^[\t\w]*\\"
    var_dec = r"^[\t\w]*\b(?:(?:auto\s*|const\s*|unsigned\s*|signed\s*|register\s*|volatile\s*|static\s*|void\s*|short\s*|long\s*|char\s*|int\s*|float\s*|double\s*|_Bool\s*|complex\s*)+)(?:\s+\*?\*?\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*[\[;,=)]"
    empty = r"^\s*$"
    start = 0
    num = 1
    is_asm = False
    content = ""
    for line in lines:
        if is_asm and re.match(end_asm, line):
            Section(begin=start, end=num, file=file, content=content)
            is_asm = False
        elif is_asm:
            content += line
        elif re.match(start_asm, line) is not None:
            is_asm = True
            start = num
            content += line
        elif re.match(directive, line) is not None:
            Section(begin=num, end=num, file=file, content=line)
        elif re.match(comment, line) is not None:
            Section(begin=num, end=num, file=file, content=line)
        elif re.match(var_dec, line) is not None:
            Section(begin=num, end=num, file=file, content=line)
        elif re.match(empty, line) is not None:
            Section(begin=num, end=num, file=file, content=line)
        else:
            Section(begin=num, end=num, file=file, content=line)

        num += 1