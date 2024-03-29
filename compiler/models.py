from datetime import datetime
from django.db import models
from django.contrib.auth.models import User


class Directory(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(blank=True, max_length=150)
    creation_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('Directory', on_delete=models.CASCADE, null=True, blank=True, default=None)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def set_folder_inactive(self):
        self.active = False
        self.save()
        for file in self.file_set.all():
            file.active = False
            file.save()
        for subfolder in self.directory_set.all():
            subfolder.set_folder_inactive()

    def change_mod_date_upstream(self):
        self.save()
        if self.parent is not None:
            self.parent.change_mod_date_upstream()


class File(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(blank=True, max_length=150)
    creation_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(Directory, on_delete=models.CASCADE, null=True, blank=True, default=None)
    active = models.BooleanField(default=True)
    code = models.TextField(blank=True, default="// type your code here", null=True)

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=32, blank=True)
    description = models.CharField(blank=True, max_length=150)
    creation_date = models.DateField(auto_now_add=True)
    begin = models.IntegerField()
    end = models.IntegerField()
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('Section', on_delete=models.CASCADE, null=True, blank=True, default=None)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Type(models.TextChoices):
        ASM_INPUT = "ASM", "Asm Input"
        DIRECTIVE = "D", "Directive"
        VARIABLE = "VAR", "Variable Declaration"
        EMPTY = "EMP", "Empty Line"
        COMMENT = "COM", "Comment"
        PROCEDURE = "PRC", "Procedure"
    type = models.CharField(max_length=3, choices=Type.choices, default=Type.PROCEDURE)

    class Status(models.IntegerChoices):
        OK = 0
        ERR = 1
        WAR = 2
    status = models.IntegerField(choices=Status.choices, default=Status.OK)
    data = models.IntegerField(blank=True, default=None, null=True)

    def __str__(self):
        return str(self.file) + " " + self.name

